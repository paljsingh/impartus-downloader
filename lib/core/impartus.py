import os
import re
import sys
import time
from functools import partial

import requests
import platform

from lib.config import Config, ConfigType
from lib.core.backpackslides import BackpackSlides
from lib.core.flippedvideo import FlippedVideo
from lib.core.regularvideo import RegularVideo
from lib.threadlogging import ThreadLogger
from lib.utils import Utils
from lib.media.encoder import Encoder
from lib.media.m3u8parser import M3u8Parser
from lib.media.decrypter import Decrypter
from lib.variables import Variables

from urllib3.util.retry import Retry
from requests.adapters import HTTPAdapter
from http import HTTPStatus
from requests.exceptions import ConnectTimeout, ConnectionError, Timeout


class Impartus:
    """
    wrapper methods to authenticate and fetch content from impartus platorm.
    TODO: move the content aggregation / restructuring logic out of this class.
    """
    thread_logger = ThreadLogger(__name__)

    def __init__(self, token=None):
        self.session = None
        self.token = None

        self.logger = self.__class__.thread_logger.logger
        self.conf = Config.load(ConfigType.IMPARTUS)

        self.timeouts = tuple([
            self.conf.get('connect_timeout', 5.0),
            self.conf.get('read_timeout', 5.0)
        ])

        # reuse the auth token, if we are already authenticated.
        if token:
            self.token = token
            self.session = self._get_session_with_retry()
            self.session.cookies.update({'Bearer': token})
            self.session.headers.update({'Authorization': 'Bearer {}'.format(token)})

        # save the files here.
        platform_name = platform.system()
        self.download_dir = self.conf.get('target_dir').get(platform_name)

        self.temp_downloads_dir = os.path.join(Utils.get_temp_dir(), 'impartus.media')
        os.makedirs(self.temp_downloads_dir, exist_ok=True)

    def _download_m3u8(self, master_url):
        response = self.session.get(master_url, timeout=self.timeouts)

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
            response = self.session.get(m3u8_urls[0], timeout=self.timeouts)
            if response.status_code == 200:
                return response.text.splitlines()

    def download_m3u8_flipped(self, fcid, flipped_lecture_quality='highest'):
        root_url = Variables().login_url()
        master_url = '{}/api/fetchvideo?fcid={}&token={}&type=index.m3u8'.format(root_url, fcid, self.token)

        m3u8_urls = self._download_m3u8(master_url)
        if flipped_lecture_quality == 'highest':
            url = Utils.get_url_for_highest_quality_video(self.conf, m3u8_urls)
        elif flipped_lecture_quality == 'lowest':
            url = Utils.get_url_for_lowest_quality_video(self.conf, m3u8_urls)
        else:  # given a specific resolution.
            url = Utils.get_url_for_resolution(m3u8_urls, flipped_lecture_quality)

        if url:
            response = self.session.get(url, timeout=self.timeouts)
            if response.status_code == 200:
                return response.text.splitlines()

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
            last_percent = 0
            for track_index, track_info in enumerate(tracks_info):
                self.logger.info("[{}]: Downloading streams for track {} ..".format(rf_id, track_index))
                streams_to_join = list()
                for item in track_info:

                    # download encrypted stream..
                    enc_stream_filepath = '{}/{}'.format(download_dir, item['file_number'])
                    temp_files_to_delete.add(enc_stream_filepath)

                    if not os.path.exists(enc_stream_filepath) or os.path.getsize(enc_stream_filepath) == 0:
                        download_flag = False
                        while not download_flag:
                            if pause_ev and pause_ev.is_set():
                                self.logger.info("[{}]: Pausing download for {}".format(rf_id, mkv_filepath))
                                resume_ev.wait()
                                self.logger.info("[{}]: Resuming download for {}".format(rf_id, mkv_filepath))
                                resume_ev.clear()
                            try:
                                content = requests.get(item['url'], timeout=self.timeouts).content
                                download_flag = True
                                with open(enc_stream_filepath, 'wb') as fh:
                                    fh.write(content)
                            except (ConnectionError, Timeout, ConnectTimeout):
                                self.logger.warning("[{}]: Timeout error. retrying download for {}...".format(
                                    rf_id, item['url']))
                                time.sleep(self.conf.get('retry_wait'))

                    # decrypt files if encrypted.
                    if item.get('encryption_method') == "NONE":
                        streams_to_join.append(enc_stream_filepath)
                    else:
                        decrypted_stream_filepath = '{}.ts'.format(enc_stream_filepath)
                        if not os.path.exists(decrypted_stream_filepath) or os.path.getsize(decrypted_stream_filepath) == 0:
                            if not encryption_keys.get(item['encryption_key_id']):
                                key = self.session.get(item['encryption_key_url'], timeout=self.timeouts).content[2:]
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
                    try:
                        if progress_callback_func and items_processed_percent > last_percent:
                            progress_callback_func(items_processed_percent)
                            last_percent = items_processed_percent
                    except RuntimeError as ex:
                        self.logger.warning("Download interrupted - {}".format(ex))
                        return False

                # All stream files for this track are decrypted, join them.
                self.logger.debug("[{}]: Joining streams for track {} ..".format(rf_id, track_index))
                ts_file = Encoder.join(streams_to_join, download_dir, track_index)
                ts_files.append(ts_file)
                temp_files_to_delete.add(ts_file)

            # Encode all ts files into a single output mkv.
            os.makedirs(os.path.dirname(mkv_filepath), exist_ok=True)
            flag = Encoder.encode_mkv(rf_id, ts_files, mkv_filepath, duration, debug=self.conf.get('debug'),
                                      priority=self.conf.get('external_process_priority'))

            if flag:
                self.logger.info("[{}]: Processed {}\n---".format(rf_id, mkv_filepath))

                # delete temp files.
                if not self.conf.get('debug'):
                    Utils.delete_files(list(temp_files_to_delete))
                    os.rmdir(download_dir)
            return flag

    def get_slides(self, subjects):
        mappings = Config.load(ConfigType.MAPPINGS)
        for subject in subjects:
            root_url = Variables().login_url()
            subject_id = subject.get('subjectId')
            response = self.session.get('{}/api/subjects/backpack/{}/sessions/{}'.format(
                root_url, subject_id, subject.get('sessionId')),
                timeout=self.timeouts
            )
            if response.status_code == 200:
                backpack_slides = response.json()
                if backpack_slides:
                    for backpack_slide in backpack_slides:
                        backpack_slide['professorName'] = subject['professorName'].strip()
                        backpack_slide['subjectName'] = subject['subjectName'].strip()

                        backpack_slide['subjectNameShort'] = backpack_slide['subjectName']
                        if mappings.get(subject['subjectName']):
                            backpack_slide['subjectNameShort'] = mappings.get(backpack_slide['subjectName'])
                        backpack_slide['ext'] = backpack_slide['filePath'].split('.')[-1]
                        pattern = r'.{}$'.format(re.escape(backpack_slide['ext']))
                        backpack_slide['fileName'] = re.sub(pattern, '', backpack_slide['fileName'])

                    yield subject, backpack_slides

    def get_subjects(self):
        root_url = Variables().login_url()
        response = self.session.get('{}/api/subjects'.format(root_url), timeout=self.timeouts)
        if response.status_code == 200:
            return response.json()
        else:
            return []

    def get_chats(self, video_metadata):
        root_url = Variables().login_url()
        chat_url = '{}/api/videos/{}/chat'.format(root_url, video_metadata['ttid'])
        self.logger.info('[{}]: Downloading lecture chats from {}'.format(video_metadata['ttid'], chat_url))
        response = self.session.get(chat_url, timeout=self.timeouts)

        if response.status_code == 200:
            return response.json()
        else:
            self.logger.info("[{}]: No lecture chats found for {}".format(video_metadata['ttid'], chat_url))
            return []

    def _get_session_with_retry(self):
        session = requests.Session()
        retries = Retry(
            total=self.conf.get('max_retries', 3),  # number of retries
            backoff_factor=1.0,                     # retry after 1.0, 2.0, 3.0 ... seconds
            status_forcelist=[
                # 4xx
                HTTPStatus.REQUEST_TIMEOUT,
                HTTPStatus.TOO_MANY_REQUESTS,

                # 5xx
                HTTPStatus.INTERNAL_SERVER_ERROR,
                HTTPStatus.BAD_GATEWAY,
                HTTPStatus.SERVICE_UNAVAILABLE,
                HTTPStatus.GATEWAY_TIMEOUT,
            ])

        adapter_options = {
            'pool_connections': self.conf.get('pool_connections', 5),
            'pool_maxsize': self.conf.get('pool_maxsize', 5),
            'max_retries': retries,
        }

        # retry/timeout only for impartus site.
        session.mount(Variables().login_url(), HTTPAdapter(**adapter_options))
        return session

    def login(self):
        root_url = Variables().login_url()
        username = Variables().login_email()
        password = Variables().login_password()

        self.session = self._get_session_with_retry()
        data = {
            'username': username,
            'password': password
        }
        url = '{}/api/auth/signin'.format(root_url)
        self.logger.info('Logging in to {} with username {}.'.format(url, username))
        response = self.session.post(url, json=data, timeout=self.timeouts)
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

    def get_lecture_videos(self, subjects):
        yield from RegularVideo(subjects, self.session, self.timeouts).get_lectures()
        yield from FlippedVideo(subjects, self.session, self.timeouts).get_lectures()

    def download_slides(self, file_url, filepath):
        return BackpackSlides(self.token, self.timeouts, self.logger, self.conf)\
            .download_slides(file_url, filepath)
