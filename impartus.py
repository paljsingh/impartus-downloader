#!/usr/bin/python3
import os
from collections import defaultdict

import ffmpeg
from Crypto.Cipher import AES
import re
from urllib.parse import unquote
from shutil import copyfile
from browser import BrowserFactory
from config import Config
from utils import Utils


class Impartus:

    def __init__(self):
        self.conf = Config.load()
        self.browser = BrowserFactory.get_browser(self.conf.get('browser'))
        self.download_dir = self.conf.get('target_dir')

    def mkv_file_path(self, ttid, metadata):
        """
        If the browser objectstorage has media information, use it to create filepath,
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

    def _decrypt(self, encryption_key, in_filepath, out_filepath):  # noqa
        if encryption_key:
            if type(encryption_key) == str:
                dec_key_bytes = bytes(encryption_key, 'utf-8')
            elif type(encryption_key) == bytes:
                dec_key_bytes = encryption_key
            else:
                assert False, "Implement handling for type {}".format(type(encryption_key))

            iv = bytes('\0' * 16, 'utf-8')
            with open(out_filepath, 'wb+') as out_fh:
                with open(in_filepath, 'rb') as in_fh:
                    ciphertext = in_fh.read()
                    aes = AES.new(dec_key_bytes, AES.MODE_CBC, iv)
                    out_fh.write(aes.decrypt(ciphertext))
        else:
            # no encryption, simply copy the file.
            copyfile(in_filepath, out_filepath)

    def _join(self, files_list_by_view, out_dir):  # noqa
        """
        decrypt aes-128 bit encrypted files using the decryption key and iv=0,
        and join them into a single file.
        :param ttid: video ttid
        :param files_list_by_view: list of stream files.
        :param out_dir: output directory where the temp decrypted file
        will be stored.
        :return: return a temporary file combining all the decrypted media files.
        """
        out_files = []
        print("joining streams ..")
        for index, view in enumerate(files_list_by_view):
            out_filepath = os.path.join(out_dir, str(index) + ".ts")
            out_files.append(out_filepath)
            with open(out_filepath, 'wb+') as out_fh:
                for file in view:
                    with open(os.path.join(self.browser.media_directory(), file), 'rb') as in_fh:
                        out_fh.write(in_fh.read())
                    os.unlink(file)

        return out_files

    def split_into_tracks(self, ts_files, duration):    # noqa
        print("splitting into tracks...")
        # take out splices from file 0 and create files 1 .. n
        for index in range(1, len(ts_files)):
            start_ss = index * duration
            os.system("ffmpeg -y -loglevel quiet -i {} -c copy  -ss {} -t {} {}".format(ts_files[0], start_ss, duration, ts_files[index]))

        # trim file 0
        os.system("ffmpeg -y -loglevel quiet -i {} -c copy  -ss {} -t {} {}".format(ts_files[0], 0, duration, ts_files[0]+".ts"))
        os.rename(ts_files[0]+".ts", ts_files[0])

    def encode_mkv(self, media_files_by_view, filepath, duration):  # noqa
        """
        encode to mkv using ffmpeg.
        :param media_files_by_view: list of files to be decrypted.
        :param filepath: path of the mkv file to be created.
        :param duration: duration from the metadata.
        :return: True if encode successful.
        """
        tmp_ts_files = self._join(media_files_by_view, os.path.dirname(filepath))
        tmp_ts_files.sort(key=lambda f: os.stat(f).st_size, reverse=True)

        try:
            # ffmpeg -i in1.ts -i in2.ts ..  -c copy -map 0 -map 1 ..  $outfile
            in_args = list()
            map_args = list()

            split_flag = False
            for index, tmp_ts_file in enumerate(tmp_ts_files):
                in_args.append("-i {}".format(tmp_ts_file))
                map_args.append("-map {}".format(index))
                if os.stat(tmp_ts_file).st_size == 0:
                    split_flag = True

            if split_flag:
                self.split_into_tracks(tmp_ts_files, duration)

            os.system("ffmpeg -y -loglevel quiet {} -c copy {} {}".format(' '.join(in_args), ' '.join(map_args), filepath))
        except Exception as ex:
            print("ffmpeg exception: {}".format(ex))
            print("check the ts file(s) generated at location: {}".format(', '.join(tmp_ts_files)))
            return False

        for tmp_ts_file in tmp_ts_files:
            os.unlink(tmp_ts_file)

        return True

    def get_decrypted_media_files_by_channels(self, ttid, media_files, m3u8_content, number_of_views, duration):
        encryption_key = None
        media_files_by_view = [list() for x in range(number_of_views)]
        duration_view = defaultdict(lambda: 0)

        current_view = 0
        current_file = -1
        for content_line in m3u8_content:

            if str(content_line).startswith("#EXT-X-KEY:METHOD"):  # encryption algorithm
                method = re.sub(r"^#EXT-X-KEY:METHOD=([A-Z0-9-]+).*$", r"\1", content_line)
                if method == "NONE":
                    encryption_key = None
                else:
                    current_file += 1
                    encryption_key_filepath = os.path.join(self.browser.media_directory(), media_files[current_file])
                    encryption_key = self.browser.get_encryption_key(encryption_key_filepath)
            elif str(content_line).startswith("#EXTINF:"):  # duration
                duration_view[current_view] += float(re.sub(r'^#EXTINF:([0-9]+\.[0-9]+),.*', r"\1", content_line))
            elif str(content_line).startswith("http"):  # media file
                current_file += 1
                assert current_file < len(media_files)

                in_filepath = os.path.join(self.browser.media_directory(), media_files[current_file])
                out_filepath = os.path.join(self.download_dir, media_files[current_file])

                print("decrypting .. ")
                self._decrypt(encryption_key, in_filepath, out_filepath)
                media_files_by_view[current_view].append(out_filepath)
            elif str(content_line).startswith("#EXT-X-DISCONTINUITY"):
                # do we need anything here ?
                pass
            elif str(content_line).startswith("#EXT-X-ENDLIST"):    # end of streams
                break
            elif str(content_line).startswith("#EXT-X-MEDIA-SEQUENCE"):    # switch view
                current_view = int(re.sub("#EXT-X-MEDIA-SEQUENCE:", '', content_line))
            else:
                continue

        return media_files_by_view

    def process_videos(self):
        """
        Download videos and decrypt, encode to mkv
        :return: 
        """

        print("Files will be saved at: {}".format(self.download_dir))
        count = 0
        for metadata_item, stream_results in self.browser.get_downloads():
            # metadata has a ttid field, which should be ideal choice to use.
            # However in more than one occasions I found it to be incorrect,
            # and object store not having any matching streams.
            # Hence the crude way...
            ttid = re.sub("^.*/([0-9]{6,})[_/].*$", r"\1", metadata_item['filePath'])

            number_of_channels = metadata_item['tapNToggle']
            duration = metadata_item['actualDuration']
            m3u8_content = None
            search_for = 'ttid={}'.format(ttid)
            for stream_result in stream_results:
                if search_for in stream_result:
                    m3u8_content = stream_result.split("\n")
                    break

            media_files = self.browser.get_media_files(ttid)
            media_files_by_view = self.get_decrypted_media_files_by_channels(ttid, media_files, m3u8_content, number_of_channels, duration)

            count += 1
            filepath = self.mkv_file_path(ttid, metadata_item)
            if os.path.exists(filepath) and not self.conf.get('overwrite'):
                print("{}. File {} exists, skipping.".format(count, filepath))
            else:
                # create a mkv file at this location, use ttid, content (enc_key + filelist)
                retval = self.encode_mkv(media_files_by_view, filepath, duration)
                if retval:
                    print("{}. {}".format(count, filepath))


if __name__ == '__main__':
    impartus = Impartus()
    impartus.process_videos()
