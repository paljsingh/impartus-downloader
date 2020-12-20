#!/usr/bin/python3
import os
from browser import BrowserFactory
from config import Config
from utils import Utils
from encoder import Encoder
from m3u8parser import M3u8Parser
from decrypter import Decrypter


class Impartus:

    def __init__(self):
        self.conf = Config.load()
        self.browser = BrowserFactory.get_browser(self.conf.get('browser'))
        self.download_dir = self.conf.get('target_dir')
        self.media_directory = self.browser.media_directory()
        os.makedirs(self.conf.get('tmp_dir'), exist_ok=True)

    def mkv_file_path(self, ttid, metadata):
        """
        If the metadata object has media information, use it to create filepath,
        else create filepath using video ttid.
        :param ttid:
        :param metadata:
        :return: filepath of the mkv file.
        """
        # default new path.
        filepath = os.path.join(self.download_dir, str(ttid) + ".mkv")

        if metadata:
            metadata = Utils.sanitize(metadata)
            filepath = self.conf.get('name_format').format(**metadata, target_dir=self.download_dir)

        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        return filepath

    def process_videos(self):
        """
        Download videos and decrypt, encode to mkv
        :return: 
        """
        processed_videos = dict()

        print("Files will be saved at: {}".format(self.download_dir))
        print("---\n")

        for metadata_item, m3u8_content in self.browser.get_downloads(processed_videos):
            ttid = self.browser.get_ttid(metadata_item)
            processed_videos[ttid] = False

            # full path of the mkv file to be created.
            mkv_filepath = self.mkv_file_path(ttid, metadata_item)

            # Skip if we already have a file there (unless overwrite option set)
            if os.path.exists(mkv_filepath) and not self.conf.get('overwrite'):
                print("File {} exists, skipping.".format(mkv_filepath))
                print("---\n")
                processed_videos[ttid] = True
                continue

            # collect metadata like no-of-tracks, duration.
            number_of_tracks = int(metadata_item['tapNToggle'])
            duration = int(metadata_item['actualDuration'])

            # list of media files on disk for this download.
            # includes stream files + key files.
            media_files = self.browser.get_media_files(ttid)

            # Parse the m3u8 content and validate against the media files.
            summary, tracks_info = M3u8Parser(m3u8_content, num_tracks=number_of_tracks).parse()
            if len(media_files) != summary['total_files']:
                print("{}".format(mkv_filepath))
                print("number of media files needed {}, actual found {}".format(
                    summary['media_files'], len(media_files)))
                print("This is likely due to browser cache being full.")
                print("Delete some of the downloaded videos and try downloading again.")
                print("---\n")
                continue

            # All good.
            # Decrypt files, join media streams and encode to mkv
            ts_files = []

            if summary.get('key_files') > 0:
                print("decrypting streams .. ")

            temp_files_to_delete = list()
            for track_index, track_info in enumerate(tracks_info):
                streams_to_join = list()
                for item in track_info:

                    # decrypt files if encrypted.
                    stream_filepath = os.path.join(self.browser.media_directory(), media_files[item['file_number']])

                    if item.get('encryption_method') == "NONE":
                        streams_to_join.append(stream_filepath)
                    else:
                        encryption_key_file = os.path.join(
                            self.browser.media_directory(), media_files[item.get('encryption_key_file')]
                        )
                        encryption_key = Utils.read_file(encryption_key_file)
                        decrypted_stream_filepath = Decrypter.decrypt(
                            encryption_key, stream_filepath, self.conf.get('tmp_dir'))
                        streams_to_join.append(decrypted_stream_filepath)
                        temp_files_to_delete.append(decrypted_stream_filepath)

                # All stream files for this track are decrypted, join them.
                print("joining streams for track {} ..".format(track_index))
                ts_file = Encoder.join(streams_to_join, self.conf.get('tmp_dir'), track_index)
                ts_files.append(ts_file)
                temp_files_to_delete.append(ts_file)

            # Encode all ts files into a single output mkv.
            success = Encoder.encode_mkv(ts_files, mkv_filepath, duration, self.conf.get('debug'))

            if success:
                processed_videos[ttid] = True
                print("{}. {}".format(len(processed_videos), mkv_filepath))
                print("---\n")

                # delete temp files.
                if not self.conf.get('debug'):
                    Utils.delete_files(temp_files_to_delete)


if __name__ == '__main__':
    impartus = Impartus()
    impartus.process_videos()
