from browser.IBrowser import IBrowser
import os
import re
import sqlite3
from shutil import copyfile

from utils import Utils, CompareType


class Firefox(IBrowser):

    def __init__(self, profile_dir: str):
        self.profile_dir = profile_dir
        self._local_storage = None
        self._indexed_db = None
        self._media_directory = None

    def local_storage(self):
        """
        Return path to local storage sqlite db used by this browser.
        :return:
        """
        if self._local_storage:
            return self._local_storage

        search_for = "webappsstore.sqlite"
        storage = Utils.find_file(search_for, self.profile_dir, CompareType.EQ)

        # make a copy, as it may be locked.
        self._local_storage =  storage + ".copy"
        copyfile(storage, self._local_storage)

        return self._local_storage

    def indexed_db(self):
        """
        return path to indexed db sqlite file used by this browser for impartus site.
        :return:
        """
        if self._indexed_db:
            return self._indexed_db

        search_for = "impartus"
        indexed_db_dir = Utils.find_dir(search_for, self.profile_dir, CompareType.CONTAINS)
        indexed_db = Utils.find_file(".sqlite", indexed_db_dir, CompareType.ENDS_WITH)

        # make a copy, as it may be locked.
        self._indexed_db = indexed_db + ".copy"
        copyfile(indexed_db, self._indexed_db)

        return self._indexed_db

    def media_directory(self):
        """
        Return location of directory that holds the offline videos.
        :return:
        """
        if self._media_directory:
            return self._media_directory

        search_for = "impartus"
        indexed_db_dir = Utils.find_dir(search_for, self.profile_dir, CompareType.CONTAINS)
        self._media_directory = Utils.find_dir(".files", indexed_db_dir, CompareType.ENDS_WITH)
        return self._media_directory

    def ttid_key_files(self):
        """
        Return a tuple containing ttid, decryption key  and list of encrypted files.
        :return:
        """
        key_query = "select file_ids, key from object_data where key like '%::::';"
        file_ids_query = "select file_ids from object_data where key like '%0{}0%';"
        conn = sqlite3.connect(self.indexed_db())

        for result in conn.execute(key_query):
            file_id = result[0]
            encryption_key = self.get_encryption_key(self.media_directory(), file_id)

            # obfuscated ttid => real ttid conversion
            # 5279946 => 4168835,  52::746 => 4199635
            obfuscated_ttid = re.search(b'([:0-9][:0-9]+)', result[1]).groups()[0]
            ttid = ''.join([chr(ord(chr(x)) - 1) for x in obfuscated_ttid])

            conn1 = sqlite3.connect(self.indexed_db())
            q = file_ids_query.format(obfuscated_ttid.decode("utf-8"))
            file_results = conn1.execute(q)

            yield ttid, encryption_key, [x[0] for x in file_results.fetchmany(0)]
