from selenium.common.exceptions import TimeoutException
from selenium.webdriver.firefox.options import Options
from typing import Dict
import random

from browser.IBrowser import IBrowser
import os
import time
import sqlite3
from shutil import copyfile, rmtree
from selenium import webdriver
import contextlib
import selenium.webdriver.support.ui as ui
import logging
import re
from config import Config
from utils import Utils, CompareType


class Firefox(IBrowser):

    indexeddb_get = '''
    async function indexeddbGet() {{
        return new Promise(function(resolve, reject) {{
            var db = window.indexedDB;
            var value = [];
            openreq = db.open("{database}", 1);
            openreq.onsuccess = function (ev) {{
                db = ev.target.result;
                window.setTimeout(getResults, 1000);
            }};
            function getResults() {{
                db.transaction("{table}").objectStore("{table}").get("{item_key}").onsuccess = storeResults;
            }};
            function storeResults(ev) {{
                value = ev.target.result;
                resolve(value);
                console.log(value);
                window.setTimeout(closeDb, 1000);
            }};
            function closeDb() {{
                db.close();
            }};
        }});
    }};
    return indexeddbGet();
    '''

    indexeddb_get_all = '''
    async function indexeddbGetAll() {{
        return new Promise(function(resolve, reject) {{
            var db = window.indexedDB;
            var value = [];
            openreq = db.open("{database}", 1);
            openreq.onsuccess = function (ev) {{
                db = ev.target.result;
                window.setTimeout(getResults, 1000);
            }};
            function getResults() {{
                db.transaction("{table}").objectStore("{table}").getAll().onsuccess = storeResults;
            }};
            function storeResults(ev) {{
                value = ev.target.result;
                resolve(value);
                console.log(value);
                window.setTimeout(closeDb, 1000);
            }};
            function closeDb() {{
                db.close();
            }};
        }});
    }};
    return indexeddbGetAll();
    '''

    _media_directory = None
    _indexed_db = None

    def __init__(self):
        self.impartus_url = "https://a.impartus.com"
        self.profile_dir = os.path.join(os.environ.get('HOME'), "profile.impartus")
        self.conf = Config().config
        self.driver = None

        # dictionary of { ttid1: [file1, file2 ..], ttid2: [file101, file102 ..], .. }
        self.media_files = dict()

        os.makedirs(self.profile_dir, exist_ok=True)

        # remove any rust_mozprofile* directories under profile_directory.
        for item in os.listdir(self.profile_dir):
            dirname = os.path.join(self.profile_dir, item)
            print("deleting .. {}".format(dirname))
            if os.path.isdir(dirname) and "rust_mozprofile" in item:
                rmtree(dirname)

    def get_downloads(self, processed: Dict) -> Dict:

        # ensure firefox/geckodriver creates profile under the profile directory.
        os.environ['TMPDIR'] = self.profile_dir     # linux/mac
        os.environ['TEMP'] = self.profile_dir     # windows

        options = Options()
        size_in_kb = self.conf['cache_size_in_gb'] * 1024 * 1024
        options.set_preference(name='browser.cache.disk.capacity', value=size_in_kb)
        with contextlib.closing(webdriver.Firefox(options=options)) as driver:

            self.driver = driver
            driver.get(self.impartus_url)
            wait = ui.WebDriverWait(driver, 86400)
            wait.until(lambda drv: driver.find_elements_by_class_name('dashboard-content'))

            driver.set_script_timeout(60)

            while True:
                try:
                    time.sleep(15)

                    to_process = list()
                    metadata_results = driver.execute_script(self.indexeddb_get_all.format(
                        database="video_database", table="video_list"
                    ))

                    for indexeddb_id, metadata in enumerate(metadata_results):
                        ttid = self.get_ttid(metadata)
                        if metadata['downloaded'] and not processed.get(ttid):
                            to_sleep = False
                            m3u8_path = re.sub(
                                r"^.*m3u8=http.*%2F(download.*\.m3u8)", r"\1", metadata['m3u8Path']
                            )

                            stream_results = driver.execute_script(self.indexeddb_get.format(
                                database="video_database", table="video_data", item_key=m3u8_path
                            ))

                            if stream_results:
                                to_process.append([metadata, stream_results.split("\n")])

                    # return an item at random, so that we are not stuck retrying the same item.
                    if len(to_process) > 0:
                        num = random.randint(0, len(to_process)-1)
                        yield to_process[num]

                except TimeoutException as tex:
                    print("timeout exception : {}".format(tex))
                    continue
                except Exception:
                    logging.exception("Exception occurred.")
                    driver.quit()
                    return

    def get_media_files(self, ttid: int):
        obfuscated_ttid = ''.join([chr(ord(x) + 1) for x in str(ttid)])

        file_ids_query = 'select file_ids from object_data where key like '\
            + '"%{}%" and file_ids is not NULL order by CAST (file_ids as INTEGER) ASC'.format(obfuscated_ttid)

        conn = sqlite3.connect(self.indexed_db())
        file_results = conn.execute(file_ids_query).fetchmany(0)

        self.media_files[ttid] = [x[0] for x in file_results]
        return self.media_files[ttid]

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

        search_for = "impartus"
        # there can be more than one such directories with search word.
        for search_dir in Utils.find_dirs(search_for, self.profile_dir, CompareType.CONTAINS):
            return Utils.find_dirs(".files", search_dir, CompareType.ENDS_WITH)[0]
