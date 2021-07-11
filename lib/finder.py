import json
import os
import platform
import enzyme
from typing import Dict, List

from lib.config import Config, ConfigType
from lib.metadataparser import MetadataFileParser, MetadataDictParser
from lib.threadlogging import ThreadLogger
from ui.data.configkeys import ConfigKeys


class Finder:
    """
    Class to find / aggregate offline data.
    Responsible for collecting data from previously downloaded videos, slides and chat/captions files,
    """

    def __init__(self):
        self.conf = Config.load(ConfigType.IMPARTUS)
        self.logger = ThreadLogger(self.__class__.__name__).logger
        pass

    def get_offline_content(self):
        offline_content = dict()
        count = 0
        for dirpath, subdirs, files in os.walk(self.conf.get('target_dir').get(platform.system())):
            for rf_id, video_metadata in self.get_offline_video_metadata(dirpath, files):
                if rf_id:
                    count += 1
                    backpack_slides = self.get_offline_backpack_slides(dirpath, files)
                    chats = self.get_offline_chats(dirpath, files)
                    offline_content[rf_id] = {
                        'backpack_slides': backpack_slides,
                        'chats': chats,
                        **video_metadata,
                    }
        return offline_content

    def get_offline_video_metadata(self, path: str, files: List) -> (str, Dict):
        """
        Collect the offline video data...

        For all videos found under {target_dir}/ :
            - Find the ttid/fcid embedded in the mkv file.
            - Check if we have a copy of metadata saved at {config_dir}/impartus/<ttid/fcid>.json . This will happen if the
            user has connected to impartus site at least once.

            - For any videos where {config_dir}/impartus/ does not have the metadata, try to reconstruct the fields
            from {video_path} format
                - Parse the actual file path to match the {video_path} format. This should provide some of the basic
                fields (subject, topic, lecture #, professor name etc.
                - Fill in the remaining fields with default values, or extract from the video file if possible.
        """

        for filename in files:
            if not filename.endswith('.mkv'):
                continue
            filepath = os.path.join(path, filename)
            rf_id, flipped = self._get_rfid(filepath)
            if rf_id:
                try:
                    metadata_file = '{}/{}.json'.format(
                        self.conf.get(ConfigKeys.CONFIG_DIR.value).get(platform.system()),
                        rf_id
                    )
                    # if json file is present ...
                    if os.path.exists(metadata_file):
                        with open(metadata_file, 'r') as fh:
                            video_metadata = json.load(fh)
                    else:
                        # parse from the file path.
                        parsed_items = MetadataFileParser.parse_from_filepath(filepath, ConfigKeys.VIDEO_PATH.value)
                        video_metadata = MetadataDictParser.sanitize(parsed_items)
                        if flipped:
                            video_metadata['fcid'] = rf_id
                        else:
                            video_metadata['ttid'] = rf_id
                        video_metadata = MetadataDictParser.add_new_fields(video_metadata)

                    video_metadata['offline_filepath'] = filepath
                    yield rf_id, video_metadata

                except NameError as ex:
                    self.logger.warning('config_dir not found, or does not exist. error: {}'.format(ex))
                except SyntaxError as ex:
                    self.logger.warning('error reading metadata file: {}'.format(ex))
                except KeyError as ex:
                    self.logger.warning('error parsing offline filepath: {}'.format(ex))

        return None, None

    def get_offline_backpack_slides(self, path: str, files: List):
        backpack_slides = []
        for filename in files:
            for ext in self.conf.get('allowed_ext'):
                if filename.endswith(ext):
                    backpack_slides.append(os.path.join(path, filename))
        return backpack_slides

    def get_offline_chats(self, path: str, files: List):  # noqa
        for filename in files:
            if filename.endswith('.vtt'):
                return os.path.join(path, filename)

    def _get_rfid(self, filepath: str):
        try:
            with open(filepath, 'rb') as f:
                mkv = enzyme.MKV(f)
                if mkv.tags:
                    for x in mkv.tags:
                        for y in x.simpletags:
                            if y.name == 'TTID':
                                return int(y.string), False
                            if y.name == 'FCID':
                                return int(y.string), True
        except enzyme.MalformedMKVError as ex:
            self.logger.warning("Exception while parsing file {}".format(str(filepath)))
            self.logger.warning("You may want to delete and re-download this file.")
            self.logger.warning("Exception: {}".format(ex))
            pass


if __name__ == '__main__':
    conf = Config.load(ConfigType.IMPARTUS)
    con = Finder().get_offline_content()
    print(con)
