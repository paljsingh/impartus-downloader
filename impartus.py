#!/usr/bin/python3
import os
import ffmpeg
from Crypto.Cipher import AES
import re

from browser import BrowserFactory
from config import Config
from utils import Utils


class Impartus:

    def __init__(self):
        self.conf = Config.load()
        self.browser = BrowserFactory.get_browser(self.conf.get('browser'))
        self.download_dir = self.conf.get('target_dir')

    def mp4_file_path(self, ttid, metadata):
        """
        If the browser local storage has media information, use it to create filepath,
        else create filepath using video ttid.
        :param ttid:
        :param metadata:
        :return: filepath.
        """
        # default new path.
        filepath = os.path.join(self.download_dir, str(ttid) + ".mp4")

        metadata = Utils.sanitize(metadata)
        if metadata:
            filepath = self.conf.get('name_format').format(**metadata, target_dir=self.download_dir)

        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        return filepath

    def _decrypt_and_join(self, ttid, encryption_key, files_list, out_directory):   # noqa
        """
        decrypt aes-128 bit encrypted files using the decryption key and iv=0,
        and join them into a single file.
        :param files_list:
        :param decryption_key:
        :param ttid:
        :return: return a temporary file combining all the decrypted media files.
        """
        out_file = os.path.join(out_directory, ttid)

        if encryption_key:
            dec_key_bytes = bytes(encryption_key, 'utf-8')
            iv = bytes('\0' * 16, 'utf-8')
            with open(out_file, 'wb+') as out_fh:
                for file in files_list:
                    with open(os.path.join(self.browser.media_directory(), file), 'rb') as in_fh:
                        ciphertext = in_fh.read()
                        aes = AES.new(dec_key_bytes, AES.MODE_CBC, iv)
                        out_fh.write(aes.decrypt(ciphertext))
        else:
            # no encryption, simply join all the files.
            with open(out_file, 'wb+') as out_fh:
                for file in files_list:
                    with open(os.path.join(self.browser.media_directory(), file), 'rb') as in_fh:
                        out_fh.write(in_fh.read())

        return out_file

    def encode_mp4(self, ttid, encryption_key, media_files, filepath):  # noqa
        """
        encode to mp4 using ffmpeg.
        :param ttid:
        :param encryption_key: decryption key.
        :param media_files: list of files to be decrypted.
        :return:
        """
        tmp_ts_file = self._decrypt_and_join(ttid, encryption_key, media_files, os.path.dirname(filepath))

        try:
            # ffmpeg -i all.ts -acodec copy -vcodec copy $outfile
            stream = ffmpeg.input(tmp_ts_file)
            stream = ffmpeg.output(stream, filepath, vcodec="copy", acodec="copy")
            ffmpeg.run(stream, quiet=True)
        except Exception as ex:
            print("ffmpeg exception: {}".format(ex))
            print("check the ts file generated at location: {}".format(tmp_ts_file))
            return False

        os.unlink(tmp_ts_file)
        return True

    def process_videos(self):
        """
        Download videos and decrypt, encode to mp4
        :return:
        """

        print("Files will be saved at: {}".format(self.download_dir))
        count = 0
        for metadata_item in self.browser.get_downloads():
            ttid = re.sub("^.*/([0-9]{6,})[_/].*$", r"\1", metadata_item['filePath'])
            encryption_key, media_files = self.browser.get_media_files(ttid)

            count += 1
            filepath = self.mp4_file_path(ttid, metadata_item)
            if os.path.exists(filepath):
                print("{}. File {} exists, skipping.".format(count, filepath))
            else:
                # create a mp4 file at this location, use ttid, content (enc_key + filelist)
                self.encode_mp4(ttid, encryption_key, media_files, filepath)
                print("{}. {}".format(count, filepath))


if __name__ == '__main__':
    impartus = Impartus()
    impartus.process_videos()
