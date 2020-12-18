from abc import ABC, abstractmethod


class IBrowser(ABC):

    @abstractmethod
    def get_downloads(self):
        """
        Yields a video-metadata object corresponding to a video that has been
        successfully downloaded.
        [see Firefox -> Tools -> Web Developer -> Storage Options -> Indexed DB ->
        https://a.impartus.com -> video_database -> video_list ]
        :return: metadata object(s) from the objectstore.
        """
        pass

    @abstractmethod
    def get_media_files(self, ttid):
        """
        for a given ttid, return the media files (and encryption key, if exists)
        :param ttid:
        :return: encryption key or None, list of media filenames.
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

    def get_encryption_key(self, filepath: str):        # noqa
        """
        extract encryption key from the key-file.
        :param filepath:
        :return:
        """
        with open(filepath, 'rb') as fh:
            key = fh.read()
        return key
