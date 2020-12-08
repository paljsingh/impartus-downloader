import json
import sqlite3
from abc import ABC, abstractmethod
import os


class IBrowser(ABC):

    key_files_map = dict()

    @abstractmethod
    def local_storage(self):
        """
        Return path to local storage sqlite db used by this browser.
        :return:
        """
        pass


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

    @abstractmethod
    def ttid_key_files(self):
        """
        Return a tuple containing ttid, decryption key  and list of encrypted files.
        :return:
        """
        pass

    def get_key_files_map(self):
        """
        return a dict with mapping like:
        {
            ttid1 : {
                key: encryption_key1,
                files: [ file11, file12, file13 ... ],
            },
            ttid2 : {
                key: encryption_key2,
                files: [ file21, file22, file23 ... ],
            },
            ...
        }
        :return:
        """
        for ttid, key, files in self.ttid_key_files():
            self.add_key_files(ttid, key, files)
        return self.key_files_map

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

    def add_key_files(self, ttid, key, files):
        """
        build ttid : { key: key, files: [files] } map
        :param ttid:
        :param key:
        :param files:
        :return:
        """
        self.key_files_map[ttid] = {
            'key': key,
            'files': files
        }

    def get_metadata(self, ttid):
        """
        get video metadata from local storage.
        :param ttid:
        :return:
        """
        query = "SELECT value from webappsstore2 where key={}".format(ttid)
        result = sqlite3.connect(self.local_storage()).execute(query).fetchone()
        if result:
            return json.loads(result[0])

    # def get_profile_dir(self, platform: IPlatform):
    #     platform.