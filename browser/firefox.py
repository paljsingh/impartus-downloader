from selenium.webdriver.firefox.options import Options

from browser.IBrowser import IBrowser
import os
import sqlite3
from shutil import copyfile, rmtree
from selenium import webdriver
import contextlib
import selenium.webdriver.support.ui as ui
import time

from config import Config
from utils import Utils, CompareType


class Firefox(IBrowser):

    indexeddb_metadata_script = '''
async function indexeddb_metadata() {
    return new Promise(function(resolve, reject) {
        var db = window.indexedDB;
        var value = []
        db.open("video_database").onsuccess = function (ev) {
            db = ev.target.result;
            window.setTimeout(getSomeValue, 1000);
        };
        function getSomeValue() {
            console.log(db);
            console.log(db.objectStoreNames);
            db.transaction("video_list").objectStore("video_list").getAll().onsuccess = showValue;
        };
        function showValue(ev) {
            value = ev.target.result;
            console.log(value);
            // Don't forget to close your connections!
            db.close();
            resolve(value);
        };
    });
}
return indexeddb_metadata();
'''

    _media_directory = None
    _indexed_db = None

    def __init__(self):
        self.impartus_url = "https://a.impartus.com"
        self.profile_dir = os.path.join(os.environ.get('HOME'), "profile.impartus")
        self.conf = Config().config

        os.makedirs(self.profile_dir, exist_ok=True)

        # remove any rust_mozprofile* directories under profile_directory.
        for item in os.listdir(self.profile_dir):
            if os.path.isdir(item) and "rust_mozprofile" in item:
                rmtree(item)

    def get_downloads(self):
        processed = []

        try:
            # ensure firefox/geckodriver creates profile under the profile directory.
            os.environ['TMPDIR'] = self.profile_dir     # linux/mac
            os.environ['TEMP'] = self.profile_dir     # windows

            options = Options()
            size_in_kb = self.conf['cache_size_in_gb'] * 1024 * 1024
            options.set_preference(name='browser.cache.disk.capacity', value=size_in_kb)
            with contextlib.closing(webdriver.Firefox(options=options)) as driver:

                driver.get(self.impartus_url)
                wait = ui.WebDriverWait(driver, 3600)
                wait.until(lambda drv: driver.find_elements_by_class_name('dashboard-content'))
                while True:
                    metadata_results = driver.execute_script(self.indexeddb_metadata_script)
                    for metadata in metadata_results:
                        if metadata['downloaded'] and metadata['ttid'] not in processed:
                            yield metadata
                            processed.append(metadata['ttid'])
                    print("processed {} / {}".format(len(processed), len(metadata_results)))
                    time.sleep(20)

        except Exception as ex:
            print("browser closed. {}".format(ex))
            driver.quit()

    def get_media_files(self, ttid: str):
        obfuscated_ttid = ''.join([chr(ord(x) + 1) for x in ttid])

        key_query = 'select file_ids, key from object_data where key like "%{}%::::"'.format(obfuscated_ttid)
        file_ids_query = 'select file_ids from object_data where key like "%0{}0%" order by CAST (file_ids as INTEGER) ASC'.format(obfuscated_ttid)

        conn = sqlite3.connect(self.indexed_db())
        result = conn.execute(key_query).fetchone()

        encryption_key = None
        if result:
            file_id = result[0]
            encryption_key = self.get_encryption_key(self.media_directory(), file_id)

        file_results = conn.execute(file_ids_query).fetchmany(0)
        return encryption_key, [x[0] for x in file_results]

    def indexed_db(self):
        """
        return path to indexed db sqlite file used by this browser for impartus site.
        :return:
        """
        media_dir = self.media_directory()
        db = os.path.join(os.path.dirname(media_dir), os.path.basename(media_dir).split('.')[0] + ".sqlite")

        # make a copy, as it may be locked.
        db_copy = db + ".copy"
        copyfile(db, db_copy)
        return db_copy

    def media_directory(self):
        """
        Return location of directory that holds the offline videos.
        :return:
        """
        if self._media_directory:
            return self._media_directory

        min_media_files = 2
        search_for = "impartus"
        # there can be more than one such directories with search word.
        for search_dir in Utils.find_dirs(search_for, self.profile_dir, CompareType.CONTAINS):
            for media_directory in Utils.find_dirs(".files", search_dir, CompareType.ENDS_WITH):
                if len(os.listdir(media_directory)) > min_media_files:
                    return media_directory


if __name__ == '__main__':
    print(Firefox().get_downloads())
