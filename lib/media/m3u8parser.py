from typing import List
import re


class M3u8Parser:
    """
    m3u8 parsing logic.
    """

    def __init__(self, content_list: List = None, num_tracks=1):
        if content_list:
            self.m3u8_content = content_list
        else:
            self.m3u8_content = []

        # Tracks object is a list of lists, example:
        # [
        #  [
        #   { "file_number": 123, "duration": 7200, "encryption_key_file": "100",
        #   "encryption_method": "AES-128", 'url": 'http://...' },
        #   { "file_number": 456, "duration": 5400, "encryption_key_file": None,
        #   "encryption_method": "NONE", 'url": 'http://...' },
        #   ...
        #  ],
        #  [
        #   { "file_number": 999, "duration": 7500, "encryption_key_file": "777",
        #   "encryption_method": "AES-128", 'url": 'http://...' },
        #   { "file_number": 888, "duration": 3600, "encryption_key_file": None,
        #   "encryption_method": "NONE", 'url": 'http://...' },
        #   ...
        #  ],
        # ]
        #
        # Above example is a 2-track file with track 0 consisting of stream files 123, 456, ...
        # and track 1 consisting of stream files 999, 888, ...
        # Of these, streams 123 and 999 are encrypted, encryption keys stored in file 100 and 777
        # respectively.
        self.tracks = [list() for x in range(num_tracks)]   # noqa

        # Summary object to provide a summary of m3u8 parsed content.
        self.summary = dict()

    def parse(self):
        """
        Parse the m3u8 file and create mapping of stream files to their encryption algorithm and encryption key file.
        Also, populate the summary object listing total number of files, number of keys and total duration.
        """

        url_maps = dict()

        current_file_number = -1
        current_file_duration = 0
        current_encryption_method = "NONE"
        current_encryption_key_url = None

        key_id = 0
        key_files = 0
        media_files = 0
        total_duration = 0
        for index, token in enumerate(self.m3u8_content):
            if str(token).startswith("#EXT-X-KEY:METHOD"):  # encryption algorithm
                current_encryption_method = re.sub(r"^#EXT-X-KEY:METHOD=([A-Z0-9-]+).*$", r"\1", token)
                if current_encryption_method == "NONE":
                    current_encryption_key_url = None
                else:
                    current_encryption_key_url = re.sub(r"^#EXT-X-KEY:METHOD=([A-Z0-9-]+).*(http.*)\"$", r"\2", token)
                    key_id = re.sub(r"^.*keyid=([0-9]+).*$", r"\1", current_encryption_key_url)
                    key_files += 1

            elif str(token).startswith("#EXTINF:"):  # duration
                current_file_duration = float(re.sub(r'^#EXTINF:([0-9]+\.[0-9]+),.*', r"\1", token))
                total_duration += current_file_duration
            elif str(token).startswith("http"):  # media file
                current_file_number += 1
                media_files += 1

                url = str(token).strip()
                base_url = self.get_base_url(url)
                if url_maps.get(base_url) is None:
                    url_maps[base_url] = len(url_maps.keys())

                current_track = url_maps[base_url]
                self.tracks[current_track].append({
                    "file_number": current_file_number,
                    "duration": current_file_duration,
                    "encryption_key_url": current_encryption_key_url,
                    "encryption_key_id": key_id,
                    "encryption_method": current_encryption_method,
                    "url": url,
                })
            else:
                continue

        self.summary = {
            "key_files": key_files,
            "media_files": media_files,
            "total_files": key_files + media_files,
            "total_duration": round(total_duration),   # combined of all tracks.
        }
        return self.summary, self.tracks

    def get_base_url(self, url: str):
        return re.sub('/[^/]+\.[a-zA-Z0-9]{2,3}$', '', url)