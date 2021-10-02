import json
import os
import platform
from datetime import datetime

import enzyme
from typing import Dict, List
import random

from lib.config import Config, ConfigType
from lib.metadataparser import MetadataFileParser, MetadataDictParser
from lib.threadlogging import ThreadLogger
from lib.data.labels import ConfigKeys
from lib.data.labels import Labels


class Finder:
    """
    Class to find / aggregate offline data.
    Responsible for collecting data from previously downloaded videos, slides and chat/captions files,
    """

    def __init__(self):
        self.conf = Config.load(ConfigType.IMPARTUS)
        self.logger = ThreadLogger(self.__class__.__name__).logger
        pass

    def get_offline_videos(self):
        count = 0
        for dirpath, subdirs, files in os.walk(self.conf.get('target_dir').get(platform.system())):
            for rf_id, video_metadata in self.get_offline_video_metadata(dirpath, files):
                if rf_id:
                    count += 1
                    chats = self.get_offline_chats(dirpath, files)
                    is_flipped = False
                    yield rf_id, video_metadata, is_flipped, chats
                    # offline_videos[rf_id] = {
                    #     'chats': chats,
                    #     **video_metadata,
                    # }
        # return offline_videos

    def get_offline_video_metadata(self, path: str, files: List) -> (str, Dict):
        """
        Collect the offline video data...

        For all videos found under {target_dir}/ :
            - Find the ttid/fcid embedded in the mkv file.
            - Check if we have a copy of metadata saved at {config_dir}/impartus/<ttid/fcid>.json .
              This will happen if the user has connected to impartus site at least once.

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

            flipped = False
            try:
                rf_id, flipped = self._get_rfid(filepath)
            except TypeError:
                rf_id = random.randint(1, int(1e6)) * -1
                pass

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
                        parsed_items = MetadataFileParser().parse_from_filepath(filepath, ConfigKeys.VIDEO_PATH.value)
                        video_metadata = MetadataDictParser().sanitize(parsed_items)
                        if flipped:
                            video_metadata['fcid'] = rf_id
                        else:
                            video_metadata['ttid'] = rf_id
                        video_metadata = MetadataDictParser().add_new_fields(video_metadata)

                    video_metadata['offline_filepath'] = filepath
                    yield rf_id, video_metadata

                except NameError as ex:
                    self.logger.warning('config_dir not found, or does not exist. error: {}'.format(ex))
                except SyntaxError as ex:
                    self.logger.warning('error reading metadata file: {}'.format(ex))
                except KeyError as ex:
                    self.logger.warning('error parsing offline filepath: {}'.format(ex))

        return None, None

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
            return None, None

    def get_offline_backpack_slides(self, mapping_by_subject_name=None):
        for dirpath, subdirs, files in os.walk(self.conf.get('target_dir').get(platform.system())):
            for filename in files:
                for ext in self.conf.get('allowed_ext'):
                    if filename.endswith(ext):
                        filepath = os.path.join(dirpath, filename)
                        parsed_fields = MetadataFileParser().parse_from_filepath(
                            filepath, ConfigKeys.DOCUMENTS_PATH.value)

                        prof_name = None
                        if parsed_fields.get('professorName'):
                            prof_name = parsed_fields['professorName']

                        subject_metadata = self._get_subject_info(parsed_fields, mapping_by_subject_name)
                        backpack_slide = {
                            'offline_filepath': filepath,
                            'fileName': filename,
                            'fileLength': os.path.getsize(filepath),
                            'fileLengthKB': os.path.getsize(filepath) // 1024,
                            'fileLengthMB': '{:.1f}'.format(os.path.getsize(filepath) / (1024 * 1024)),
                            'fileDate': datetime.fromtimestamp(os.path.getmtime(filepath)).strftime("%Y-%m-%d"),
                            'description': '',
                            'professorName': prof_name,
                            'ext': str.split(filepath, '.')[-1],
                        }
                        yield subject_metadata, backpack_slide

    def _get_subject_info(self, metadata, subject_name_id_map=None):    # noqa
        subject_id = -1
        subject_name = "No Subject"
        for name in [Labels.SUBJECT_NAME.value, Labels.SUBJECT_NAME_SHORT.value]:
            if metadata.get(name):
                subject_name = metadata[name]
                if subject_name_id_map and subject_name_id_map.get(name):
                    subject_id = subject_name_id_map[name]['subjectId']
                return {'subjectId': subject_id, 'subjectName': subject_name}
        return {'subjectId': subject_id, 'subjectName': subject_name}
