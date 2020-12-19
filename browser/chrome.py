from browser.IBrowser import IBrowser
from typing import List, Dict

# TODO: Implement for chrome


class Chrome(IBrowser):
    def get_downloads(self, processed: Dict):
        pass

    def get_media_files(self, ttid: int):
        pass

    def indexed_db(self):
        pass

    def media_directory(self):
        pass

    def __init__(self):
        pass
