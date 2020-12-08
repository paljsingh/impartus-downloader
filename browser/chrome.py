from browser.IBrowser import IBrowser

# TODO: Implement for chrome


class Chrome(IBrowser):
    def __init__(self, profile_dir: str):
        self.profile_dir = profile_dir
        pass

    def ttid_key_files(self):
        pass

    def local_storage(self):
        pass

    def indexed_db(self):
        pass

    def media_directory(self):
        pass
