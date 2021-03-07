#!/usr/bin/python3
import os
import re
from browser import BrowserFactory
from config import Config
from utils import Utils
from encoder import Encoder
from m3u8parser import M3u8Parser
from decrypter import Decrypter
import urllib

import requests


class Impartus:
    def __init__(self, token=None):
        self.session = None
        self.token = None

        # reuse the auth token, if we are already authenticated.
        if token:
            self.token = token
            self.session = requests.Session()
            self.session.cookies.update({'Bearer': token})
            self.session.headers.update({'Authorization': 'Bearer {}'.format(token)})

        self.conf = Config.load()

        # save the files here.
        if os.name == 'posix':
            self.download_dir = self.conf.get('target_dir').get('posix')
        else:
            self.download_dir = self.conf.get('target_dir').get('windows')

        self.temp_downloads_dir = os.path.join(Utils.get_temp_dir(), 'impartus.media')
        os.makedirs(self.temp_downloads_dir, exist_ok=True)

    def _download_m3u8(self, root_url, ttid):
        response = self.session.get('{}/api/fetchvideo?ttid={}&token={}&type=index.m3u8'.format(root_url, ttid, self.token))
        if response.status_code == 200:
            lines = response.text.splitlines()
            for line in lines:
                if re.match('^http', line):
                    url = line.strip()
                    response = self.session.get(url)
                    if response.status_code == 200:
                        return response.text.splitlines()
        return None

    def process_video(self, video_metadata, mkv_filepath, root_url, progress_bar_value):
        """
        Download video and decrypt, join, encode to mkv
        :return: 
        """
        ttid = video_metadata['ttid']
        number_of_tracks = int(video_metadata['tapNToggle'])
        duration = int(video_metadata['actualDuration'])
        encryption_keys = dict()

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
                            print("retrying download for {}...".format(item['url']))

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
                    progress_bar_value.set(items_processed * 100 // summary.get('total_files'))

                # All stream files for this track are decrypted, join them.
                print("joining streams for track {}..".format(track_index))
                ts_file = Encoder.join(streams_to_join, download_dir, track_index)
                ts_files.append(ts_file)
                temp_files_to_delete.add(ts_file)

            # Encode all ts files into a single output mkv.
            os.makedirs(os.path.dirname(mkv_filepath), exist_ok=True)
            success = Encoder.encode_mkv(ts_files, mkv_filepath, duration, self.conf.get('debug'))

            if success:
                print("{}".format(mkv_filepath))
                print("---\n")

                # delete temp files.
                if not self.conf.get('debug'):
                    Utils.delete_files(list(temp_files_to_delete))

    def filter_subjects(self, subjects):
        return subjects

    def get_mkv_path(self, video_metadata):
        filepath = os.path.join(self.download_dir, str(video_metadata.get('ttid')) + ".mkv")
        if video_metadata:
            filepath = self.conf.get('name_format').format(**video_metadata, target_dir=self.download_dir)
        return filepath

    def get_videos(self, root_url, subject):
        response = self.session.get('{}/api/subjects/{}/lectures/{}'.format(root_url, subject.get('subjectId'), subject.get('sessionId')))
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

    def authenticate(self, username, password, url):
        self.session = requests.Session()
        data = {
            'username': username,
            'password': password
        }
        response = self.session.post('{}/api/auth/signin'.format(url), json=data, timeout=30)
        if response.status_code == 200:
            self.token = response.json()['token']
            self.session.cookies.update({'Bearer': self.token})
            self.session.headers.update({'Authorization': 'Bearer {}'.format(self.token)})
            return True

        return False
