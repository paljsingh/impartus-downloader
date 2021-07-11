import os
import re
import time
from typing import List

import requests
import platform
from datetime import datetime, timedelta

from lib.config import Config, ConfigType
from lib.metadataparser import MetadataDictParser
from lib.threadlogging import ThreadLogger
from lib.utils import Utils
from lib.media.encoder import Encoder
from lib.media.m3u8parser import M3u8Parser
from lib.media.decrypter import Decrypter
from ui.data.configkeys import ConfigKeys
from lib.variables import Variables


class Impartus:
    """
    wrapper methods to authenticate and fetch content from impartus platorm.
    TODO: move the content aggregation / restructuring logic out of this class.
    """
    thread_logger = ThreadLogger(__name__)

    def __init__(self, token=None):
        self.session = None
        self.token = None
        self.logger = Impartus.thread_logger.logger
        # enzyme library logs too much, suppress it's logs.
        # logging.getLogger("enzyme").setLevel(logging.FATAL)

        # reuse the auth token, if we are already authenticated.
        if token:
            self.token = token
            self.session = requests.Session()
            self.session.cookies.update({'Bearer': token})
            self.session.headers.update({'Authorization': 'Bearer {}'.format(token)})

        self.conf = Config.load(ConfigType.IMPARTUS)

        # save the files here.
        platform_name = platform.system()
        self.download_dir = self.conf.get('target_dir').get(platform_name)

        # export any required variables:
        if self.conf.get('export_variables') and self.conf['export_variables'].get(platform_name):
            for key, value in self.conf['export_variables'].get(platform_name).items():
                os.environ[key] = value

        self.temp_downloads_dir = os.path.join(Utils.get_temp_dir(), 'impartus.media')
        os.makedirs(self.temp_downloads_dir, exist_ok=True)

    def _download_m3u8(self, master_url):
        response = self.session.get(master_url)
        m3u8_urls = []
        if response.status_code == 200:
            lines = response.text.splitlines()
            for line in lines:
                if re.match('^http', line):
                    m3u8_urls.append(line.strip())
        return m3u8_urls

    def download_m3u8_regular(self, ttid):
        root_url = Variables().login_url()
        master_url = '{}/api/fetchvideo?ttid={}&token={}&type=index.m3u8'.format(root_url, ttid, self.token)
        m3u8_urls = self._download_m3u8(master_url)

        if len(m3u8_urls) > 0:
            response = self.session.get(m3u8_urls[0])
            if response.status_code == 200:
                return response.text.splitlines()

    def download_m3u8_flipped(self, fcid, flipped_lecture_quality='highest'):
        root_url = Variables().login_url()
        master_url = '{}/api/fetchvideo?fcid={}&token={}&type=index.m3u8'.format(root_url, fcid, self.token)

        m3u8_urls = self._download_m3u8(master_url)
        if flipped_lecture_quality == 'highest':
            url = self.get_url_for_highest_quality_video(m3u8_urls)
        elif flipped_lecture_quality == 'lowest':
            url = self.get_url_for_lowest_quality_video(m3u8_urls)
        else:  # given a specific resolution.
            url = self.get_url_for_resolution(m3u8_urls, flipped_lecture_quality)

        if url:
            response = self.session.get(url)
            if response.status_code == 200:
                return response.text.splitlines()

    def get_url_for_highest_quality_video(self, m3u8_urls):
        for resolution in self.conf.get('flipped_lecture_quality_order'):
            for url in m3u8_urls:
                if resolution in url:
                    return url

    def get_url_for_lowest_quality_video(self, m3u8_urls):
        for resolution in reversed(self.conf.get('flipped_lecture_quality_order')):
            for url in m3u8_urls:
                if resolution in url:
                    return url

    def get_url_for_resolution(self, m3u8_urls, resolution):  # noqa
        for url in m3u8_urls:
            if resolution in url:
                return url

    def process_video(self, video_metadata, mkv_filepath, pause_ev, resume_ev, progress_callback_func,
                      video_quality='highest'):
        """
        Download video and decrypt, join, encode to mkv
        :return:
        """
        number_of_tracks = int(video_metadata['tapNToggle'])
        duration = int(video_metadata['actualDuration'])
        encryption_keys = dict()

        rf_id = video_metadata['ttid'] if video_metadata.get('ttid') else video_metadata['fcid']
        self.logger.info("[{}]: Starting download for {}".format(rf_id, mkv_filepath))
        if video_metadata.get('fcid'):
            m3u8_content = self.download_m3u8_flipped(rf_id, video_quality)
        else:
            m3u8_content = self.download_m3u8_regular(rf_id)

        # download media files for this video.
        if m3u8_content:
            summary, tracks_info = M3u8Parser(m3u8_content, num_tracks=number_of_tracks).parse()
            download_dir = os.path.join(self.temp_downloads_dir, str(rf_id))
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
                        if pause_ev.is_set():
                            self.logger.info("[{}]: Pausing download for {}".format(rf_id, mkv_filepath))
                            resume_ev.wait()
                            self.logger.info("[{}]: Resuming download for {}".format(rf_id, mkv_filepath))
                            resume_ev.clear()
                        try:
                            with open(enc_stream_filepath, 'wb') as fh:
                                content = requests.get(item['url']).content
                                fh.write(content)
                                download_flag = True
                        except TimeoutError:
                            self.logger.warning("[{}]: Timeout error. retrying download for {}...".format(
                                rf_id, item['url']))
                            time.sleep(self.conf.get('retry_wait'))

                    # decrypt files if encrypted.
                    if item.get('encryption_method') == "NONE":
                        streams_to_join.append(enc_stream_filepath)
                    else:
                        if not encryption_keys.get(item['encryption_key_id']):
                            key = self.session.get(item['encryption_key_url']).content[2:]
                            key = key[::-1]  # reverse the bytes.
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
                    progress_callback_func(items_processed_percent)

                # All stream files for this track are decrypted, join them.
                self.logger.info("[{}]: Joining streams for track {} ..".format(rf_id, track_index))
                ts_file = Encoder.join(streams_to_join, download_dir, track_index)
                ts_files.append(ts_file)
                temp_files_to_delete.add(ts_file)

            # Encode all ts files into a single output mkv.
            os.makedirs(os.path.dirname(mkv_filepath), exist_ok=True)
            success = Encoder.encode_mkv(rf_id, ts_files, mkv_filepath, duration, self.conf.get('debug'))

            if success:
                self.logger.info("[{}]: Processed {}\n---".format(rf_id, mkv_filepath))

                # delete temp files.
                if not self.conf.get('debug'):
                    Utils.delete_files(list(temp_files_to_delete))
                    os.rmdir(download_dir)

    def _get_filepath(self, video_metadata, config_key: str):
        if self.conf.get('use_safe_paths'):
            sanitized_components = MetadataDictParser.sanitize(MetadataDictParser.parse_metadata(video_metadata))
            file_path = self.conf.get(config_key).format(**{**video_metadata, **sanitized_components},
                                                         target_dir=self.download_dir)
        else:
            file_path = self.conf.get(config_key).format(**video_metadata, target_dir=self.download_dir)
        return file_path

    def get_mkv_path(self, video_metadata):
        return self._get_filepath(video_metadata, ConfigKeys.VIDEO_PATH.value)

    def get_slides_path(self, video_metadata):
        return self._get_filepath(video_metadata, ConfigKeys.SLIDES_PATH.value)

    def get_captions_path(self, video_metadata):
        return self._get_filepath(video_metadata, ConfigKeys.CAPTIONS_PATH.value)

    def slides_exist_on_disk(self, path):
        path_without_ext = path.rsplit('.', 1)[0]
        for ext in self.conf.get('allowed_ext'):
            path_with_ext = '{}.{}'.format(path_without_ext, ext)
            if os.path.exists(path_with_ext):
                return True, path_with_ext
        return False, path

    def get_lectures(self, subject):
        root_url = Variables().login_url()

        response = self.session.get('{}/api/subjects/{}/lectures/{}'.format(
            root_url, subject.get('subjectId'), subject.get('sessionId')))

        if response.status_code == 200:
            return response.json()
        else:
            return []

    def get_flipped_lectures(self, subject):
        root_url = Variables().login_url()

        flipped_lectures = []
        response = self.session.get('{}/api/subjects/flipped/{}/{}'.format(
            root_url, subject.get('subjectId'), subject.get('sessionId')))
        if response.status_code == 200:
            categories = response.json()
            for category in categories:

                # flipped lectures do not have lecture sequence number field, generate seq-no setting the oldest
                # lecture with seq-no=1. By default impartus portal return lectures with highest ttid/fcid first.
                num_lectures = len(category['lectures'])
                for i, lecture in enumerate(category['lectures']):
                    # cannot update the original dict while in loop, shallow copy is fine for now.
                    flipped_lecture = lecture.copy()
                    flipped_lecture['ttid'] = 0
                    flipped_lecture['seqNo'] = num_lectures - i
                    flipped_lecture['slideCount'] = 0
                    flipped_lecture['createdBy'] = ''  # duplicate info, present elsewhere.

                    start_time = datetime.strptime(lecture['startTime'], '%Y-%m-%d %H:%M:%S')
                    end_time = start_time + timedelta(0, lecture['actualDuration'])
                    flipped_lecture['endTime'] = end_time.strftime("%Y-%m-%d %H:%M:%S")
                    flipped_lectures.append(flipped_lecture)
        return flipped_lectures

    def get_slides(self, subject):
        root_url = Variables().login_url()
        response = self.session.get('{}/api/subjects/backpack/{}/sessions/{}'.format(
            root_url, subject.get('subjectId'), subject.get('sessionId')))
        if response.status_code == 200:
            return response.json()
        else:
            return []

    def get_subjects(self):
        root_url = Variables().login_url()
        response = self.session.get('{}/api/subjects'.format(root_url))
        if response.status_code == 200:
            return response.json()
        else:
            return []

    def get_chats(self, video_metadata):
        root_url = Variables().login_url()
        chat_url = '{}/api/videos/{}/chat'.format(root_url, video_metadata['ttid'])
        self.logger.info('[{}]: Downloading lecture chats from {}'.format(video_metadata['ttid'], chat_url))
        response = self.session.get(chat_url)

        if response.status_code == 200:
            return response.json()
        else:
            self.logger.info("[{}]: No lecture chats found for {}".format(video_metadata['ttid'], chat_url))
            return []

    def download_slides(self, rf_id, file_url, filepath):
        root_url = Variables().login_url()

        if str(file_url).startswith('http'):
            urls = re.findall(r'(https?://\S+)', file_url)
        else:
            urls = ['{}/{}'.format(root_url, file_url)]

        download_status = False
        for slides_url in urls:
            ext = slides_url.split('.')[-1].lower()
            if ext not in self.conf.get('allowed_ext'):
                self.logger.warning('[{}]: Downloading {}. Files of type {} not allowed, see config.'.format(
                    rf_id, slides_url, ext))
                continue

            self.logger.info('[{}]: Downloading slides from {}'.format(rf_id, slides_url))
            response = requests.get(slides_url, headers={'Cookie': 'Bearer={}'.format(self.token)})
            if response.status_code == 200:
                os.makedirs(os.path.dirname(filepath), exist_ok=True)

                with open(filepath, 'wb+') as fh:
                    fh.write(response.content)
                download_status = True
            else:
                self.logger.error('[{}]: Error fetching slides from url: {}'.format(rf_id, file_url))
                self.logger.error('[{}]: Http response code: {}, response body: {}: '.format(
                    rf_id, response.status_code, response.text))
        return download_status

    def map_slides_to_videos(self, videos_metadata: List, slides_metadata: List):
        """
        map all videos to corresponding backpack slides.
        return a mapping dict.
        """
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

    def login(self):
        root_url = Variables().login_url()
        username = Variables().login_email()
        password = Variables().login_password()

        self.session = requests.Session()
        data = {
            'username': username,
            'password': password
        }
        url = '{}/api/auth/signin'.format(root_url)
        self.logger.info('Logging in to {} with username {}.'.format(url, username))
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

    def logout(self):
        self.session = None
        self.token = None
        self.logger.info('Logged out from impartus!.')
        # Really Impartus? No server api to logout ?
        pass

    def is_authenticated(self):
        return True if self.session else False

    def get_online_lectures(self):
        online_lectures = dict()
        for subject in self.get_subjects():
            videos_per_subject = list()
            regular_lectures = self.get_lectures(subject=subject)
            flipped_lectures = self.get_flipped_lectures(subject=subject)

            for metadata in regular_lectures:
                online_lectures[metadata['ttid']] = MetadataDictParser.add_new_fields(metadata)
            for metadata in flipped_lectures:
                online_lectures[metadata['fcid']] = MetadataDictParser.add_new_fields(metadata)

            videos_per_subject.extend(regular_lectures)
            videos_per_subject.extend(flipped_lectures)

            slides_per_subject = self.get_slides(subject)
            mapping_dict = self.map_slides_to_videos(videos_per_subject, slides_per_subject)

            # populate the mapped slide to video metadata item.
            for item in videos_per_subject:
                rf_id = item['ttid'] if item.get('ttid') else item['fcid']
                slide_url = mapping_dict.get(rf_id)
                if slide_url:
                    online_lectures[rf_id]['slide_url'] = slide_url
                    ext = slide_url.split('.')[-1]
                    online_lectures[rf_id]['ext'] = ext
                    online_lectures[rf_id]['slide_path'] = self.get_mkv_path(item)
                else:
                    online_lectures[rf_id]['slide_url'] = ''
                    online_lectures[rf_id]['ext'] = ''
                    online_lectures[rf_id]['slide_path'] = ''

                yield online_lectures[rf_id]


class GetOutOfLoop(Exception):
    pass
