import os
import re
import time
import requests
import logging
from pathlib import Path
import enzyme

from config import Config
from utils import Utils
from encoder import Encoder
from m3u8parser import M3u8Parser
from decrypter import Decrypter


class Impartus:
    def __init__(self, token=None):
        self.session = None
        self.token = None
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(self.__class__.__name__)

        # enzyme library logs too much, suppress it's logs.
        logging.getLogger("enzyme").setLevel(logging.FATAL)

        # reuse the auth token, if we are already authenticated.
        if token:
            self.token = token
            self.session = requests.Session()
            self.session.cookies.update({'Bearer': token})
            self.session.headers.update({'Authorization': 'Bearer {}'.format(token)})

        self.conf = Config.load('impartus')

        # save the files here.
        if os.name == 'posix':
            self.download_dir = self.conf.get('target_dir').get('posix')
        else:
            self.download_dir = self.conf.get('target_dir').get('windows')

        self.temp_downloads_dir = os.path.join(Utils.get_temp_dir(), 'impartus.media')
        os.makedirs(self.temp_downloads_dir, exist_ok=True)

    def _download_m3u8(self, root_url, ttid):
        response = self.session.get('{}/api/fetchvideo?ttid={}&token={}&type=index.m3u8'.format(
            root_url, ttid, self.token))
        if response.status_code == 200:
            lines = response.text.splitlines()
            for line in lines:
                if re.match('^http', line):
                    url = line.strip()
                    response = self.session.get(url)
                    if response.status_code == 200:
                        return response.text.splitlines()
        return None

    def process_video(self, video_metadata, mkv_filepath, root_url, progress_bar_value, callback_func):
        """
        Download video and decrypt, join, encode to mkv
        :return: 
        """
        ttid = video_metadata['ttid']
        number_of_tracks = int(video_metadata['tapNToggle'])
        duration = int(video_metadata['actualDuration'])
        encryption_keys = dict()

        self.logger.info("[{}]: Starting download for {}".format(ttid, mkv_filepath))
        # download media files for this video.
        m3u8_content = self._download_m3u8(root_url, ttid)
        if m3u8_content:
            summary, tracks_info = M3u8Parser(m3u8_content, num_tracks=number_of_tracks).parse()
            download_dir = os.path.join(self.temp_downloads_dir, str(ttid))
            os.makedirs(download_dir, exist_ok=True)

            temp_files_to_delete = set()
            ts_files = list()
            items_processed = 0
            for track_index, track_info in enumerate(tracks_info):
                streams_to_join = list()
                for item in track_info:

                    # download encrypted stream..
                    enc_stream_filepath = '{}/{}'.format(download_dir, item['file_number'])
                    temp_files_to_delete.add(enc_stream_filepath)
                    download_flag = False
                    while not download_flag:
                        try:
                            with open(enc_stream_filepath, 'wb') as fh:
                                content = requests.get(item['url']).content
                                fh.write(content)
                                download_flag = True
                        except TimeoutError:
                            self.logger.warning("[{}]: Timeout error. retrying download for {}...".format(
                                ttid, item['url']))
                            time.sleep(self.conf.get('retry_wait'))

                    # decrypt files if encrypted.
                    if item.get('encryption_method') == "NONE":
                        streams_to_join.append(enc_stream_filepath)
                    else:
                        if not encryption_keys.get(item['encryption_key_id']):
                            key = self.session.get(item['encryption_key_url']).content[2:]
                            key = key[::-1]     # reverse the bytes.
                            encryption_keys[item['encryption_key_id']] = key
                        encryption_key = encryption_keys[item['encryption_key_id']]
                        decrypted_stream_filepath = Decrypter.decrypt(
                                encryption_key, enc_stream_filepath,
                                download_dir)
                        streams_to_join.append(decrypted_stream_filepath)
                        temp_files_to_delete.add(decrypted_stream_filepath)
                    # update progress bar
                    items_processed += 1
                    items_processed_percent = items_processed * 100 // summary.get('media_files')
                    callback_func(items_processed_percent)

                # All stream files for this track are decrypted, join them.
                self.logger.info("[{}]: joining streams for track {} ..".format(ttid, track_index))
                ts_file = Encoder.join(streams_to_join, download_dir, track_index)
                ts_files.append(ts_file)
                temp_files_to_delete.add(ts_file)

            # Encode all ts files into a single output mkv.
            os.makedirs(os.path.dirname(mkv_filepath), exist_ok=True)
            success = Encoder.encode_mkv(ttid, ts_files, mkv_filepath, duration, self.conf.get('debug'))

            if success:
                self.logger.info("[{}]: Processed {}\n---".format(ttid, mkv_filepath))

                # delete temp files.
                if not self.conf.get('debug'):
                    Utils.delete_files(list(temp_files_to_delete))
                    os.rmdir(download_dir)

    def get_mkv_path(self, video_metadata):
        mkv_path = self.conf.get('video_path').format(**video_metadata, target_dir=self.download_dir)
        if self.conf.get('use_safe_paths'):
            mkv_path = Utils.sanitize(mkv_path)
        return mkv_path

    def get_slides_path(self, video_metadata):
        slides_path = self.conf.get('slides_path').format(**video_metadata, target_dir=self.download_dir)
        if self.conf.get('use_safe_paths'):
            slides_path = Utils.sanitize(slides_path)
        return slides_path

    def get_mkv_ttid_map(self):
        mkv_ttid_map = dict()
        for path in Path(self.download_dir).rglob('*.mkv'):
            try:
                with open(path, 'rb') as f:
                    mkv = enzyme.MKV(f)
                    if mkv.tags:
                        for x in mkv.tags:
                            for y in x.simpletags:
                                if y.name == 'TTID':
                                    mkv_ttid_map[y.string] = str(path)
                                    raise GetOutOfLoop
            except GetOutOfLoop:
                pass
        return mkv_ttid_map

    def slides_exist_on_disk(self, path):
        path_without_ext = path.rsplit('.', 1)[0]
        for ext in self.conf.get('allowed_ext'):
            path_with_ext = '{}.{}'.format(path_without_ext, ext)
            if os.path.exists(path_with_ext):
                return True, path_with_ext
        return False, path

    def get_videos(self, root_url, subject):
        response = self.session.get('{}/api/subjects/{}/lectures/{}'.format(
            root_url, subject.get('subjectId'), subject.get('sessionId')))
        if response.status_code == 200:
            return response.json()
        else:
            return []

    def get_slides(self, root_url, subject):
        response = self.session.get('{}/api/subjects/backpack/{}/sessions/{}'.format(
            root_url, subject.get('subjectId'), subject.get('sessionId')))
        if response.status_code == 200:
            return response.json()
        else:
            return []

    def get_subjects(self, root_url):
        response = self.session.get('{}/api/subjects'.format(root_url))
        if response.status_code == 200:
            return response.json()
        else:
            return []

    def download_slides(self, ttid, file_url, filepath, root_url):
        response = requests.get('{}/{}'.format(root_url, file_url), headers={'Cookie': 'Bearer={}'.format(self.token)})
        if response.status_code == 200:
            os.makedirs(os.path.dirname(filepath), exist_ok=True)

            with open(filepath, 'wb+') as fh:
                fh.write(response.content)
            return True
        else:
            self.logger.error('[{}]: Error fetching slides from url: {}'.format(ttid, file_url))
            self.logger.error('[{}]: Http response code: {}, response body: {}: '.format(
                ttid, response.status_code, response.text))
            return False

    def map_slides_to_videos(self, videos_metadata, slides_metadata):
        mapping = dict()
        # slides upload threshold... expect slides be uploaded within N days of video upload.
        threshold_duration = self.conf.get('slides_upload_window')
        for video_item in videos_metadata:
            video_upload_date = str.split(video_item['startTime'], ' ')[0]
            for slide_item in slides_metadata:
                slide_upload_date = slide_item['fileDate']
                diff_days = Utils.date_difference(slide_upload_date, video_upload_date)
                if 0 <= diff_days <= threshold_duration:
                    mapping[video_item['ttid']] = slide_item['filePath']
        return mapping

    def authenticate(self, username, password, url):
        self.session = requests.Session()
        data = {
            'username': username,
            'password': password
        }
        url = '{}/api/auth/signin'.format(url)
        response = self.session.post(url, json=data, timeout=30)
        if response.status_code == 200:
            self.token = response.json()['token']
            self.session.cookies.update({'Bearer': self.token})
            self.session.headers.update({'Authorization': 'Bearer {}'.format(self.token)})
            return True
        else:
            self.logger.error('Error authenticating to {} with username {}.'.format(url, username))
            self.logger.error('Http response code: {}, response body: {}: '.format(response.status_code, response.text))
            return False


class GetOutOfLoop(Exception):
    pass
