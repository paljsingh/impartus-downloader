from abc import ABC, abstractmethod
from typing import List, Dict
import re


class IBrowser(ABC):

    @abstractmethod
    def get_downloads(self, processed: Dict) -> Dict:
        """
        Yields a video-metadata object corresponding to a video that has been
        successfully downloaded.
        [see Firefox -> Tools -> Web Developer -> Storage Options -> Indexed DB ->
        https://a.impartus.com -> video_database -> video_list ]
        :param processed: List of processed video ttids
        :return: metadata object(s) from the objectstore.
        """
        pass

    @abstractmethod
    def get_media_files(self, ttid: int):
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

    def get_ttid(self, metadata: Dict) -> int:  # noqa
        """
        Returns ttid from metadata item.
        :param metadata: metadata dictionary
        :return: int ttid value.
        """
        # metadata has a ttid field, which should be ideal choice to use.
        # However in more than one occasions I found it to be incorrect,
        # and object-store not having any matching streams for metadata['ttid']
        # Hence the crude way...
        return int(re.sub("^.*/([0-9]{6,})[_/].*$", r"\1", metadata['filePath']))

