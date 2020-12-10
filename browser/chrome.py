from browser.IBrowser import IBrowser

# TODO: Implement for chrome


class Chrome(IBrowser):
    def get_downloads(self):
        pass

    def get_media_files(self, ttid):
        pass

    def indexed_db(self):
        pass

    def media_directory(self):
        pass

    def __init__(self, profile_dir: str):
        self.profile_dir = profile_dir
        pass

