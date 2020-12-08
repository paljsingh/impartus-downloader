#!/usr/bin/python3
import os
import ffmpeg
from Crypto.Cipher import AES

from browser import BrowserFactory
from config import Config
from utils import Utils


class Impartus:

    def __init__(self):
        self.conf = Config.load()
        self.browser = BrowserFactory.get_browser(self.conf.get('browser'), self.conf.get('profile_dir'))

        self.download_dir = self.conf.get('target_dir')
        self.media_dir = self.browser.media_directory()

    def mp4_file_path(self, ttid):
        """
        If the browser local storage has media information, use it to create filepath,
        else create filepath using video ttid.
        :param ttid:
        :return: filepath.
        """
        # default new path.
        filepath = os.path.join(self.download_dir, ttid + ".mp4")

        if self.browser.local_storage() is not None:
            metadata = Utils.sanitize(self.browser.get_metadata(ttid))
            if metadata:
                filepath = self.conf.get('name_format').format(**metadata, target_dir=self.download_dir)

        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        return filepath

    def _decrypt_and_join(self, files_list, decryption_key, ttid):   # noqa
        """
        decrypt aes-128 bit encrypted files using the decryption key and iv=0,
        and join them into a single file.
        :param files_list:
        :param decryption_key:
        :param ttid:
        :return: return a temporary file combining all the decrypted media files.
        """
        out_file = os.path.join(self.media_dir, str(ttid))
        dec_key_bytes = bytes(decryption_key, 'utf-8')
        iv = bytes('\0' * 16, 'utf-8')
        with open(out_file, 'wb+') as out_fh:
            for file in files_list:
                with open(os.path.join(self.media_dir, file), 'rb') as in_fh:
                    ciphertext = in_fh.read()
                    aes = AES.new(dec_key_bytes, AES.MODE_CBC, iv)
                    out_fh.write(aes.decrypt(ciphertext))
        return out_file

    def encode_mp4(self, ttid, content, filepath):  # noqa
        """
        encode to mp4 using ffmpeg.
        :param ttid:
        :param content: a dict containing decryption key and list of files to be decrypted.
        :return:
        """
        tmp_ts_file = self._decrypt_and_join(content['files'], content['key'], ttid)

        # ffmpeg -i all.ts -acodec copy -vcodec copy $outfile
        stream = ffmpeg.input(tmp_ts_file)
        stream = ffmpeg.output(stream, filepath, vcodec="copy", acodec="copy")
        ffmpeg.run(stream, overwrite_output=True, quiet=True)
        os.unlink(tmp_ts_file)
        return True

    def process_videos(self):
        """
        Download videos and decrypt, encode to mp4
        :return:
        """
        key_file_map = self.browser.get_key_files_map()
        print("Files saved at: {}".format(self.download_dir))

        count = 0
        for ttid, content in key_file_map.items():
            filepath = self.mp4_file_path(ttid)
            if os.path.exists(filepath):
                print("File {} exists, skipping.".format(filepath))
            else:
                # create a mp4 file at this location, use ttid, content (enc_key + filelist)
                self.encode_mp4(ttid, content, filepath)
                count += 1
                print("{}. {}".format(count, filepath))


if __name__ == '__main__':
    impartus = Impartus()
    impartus.process_videos()
