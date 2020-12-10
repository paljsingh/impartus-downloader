import json
import sqlite3
from abc import ABC, abstractmethod
import os


class IBrowser(ABC):

    @abstractmethod
    def get_downloads(self):
        """
        Yields a video-metadata that has been downloaded completely.
        :return:
        """
        pass

    @abstractmethod
    def get_media_files(self, ttid):
        """
        for a given ttid, return the media files (and encryption key)
        :param ttid:
        :return:
        """

    @abstractmethod
    def indexed_db(self):
        """
        return path to indexed db sqlite file used by this browser for impartus site.
        :return:
        """
        pass

    @abstractmethod
    def media_directory(self):
        """
        Return location of directory that holds the offline videos.
        :return:
        """
        pass

    def get_encryption_key(self, directory: str, file: str):        # noqa
        """
        extract decryption key from the key-file.
        :param directory:
        :param file:
        :return:
        """
        with open(os.path.join(directory, file), 'r') as fh:
            key = fh.read()
        return key
