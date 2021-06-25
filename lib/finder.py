import json
import os
import platform
import logging
import re

import enzyme
from typing import Dict, List

from lib.config import Config, ConfigType
from lib.utils import Utils
from ui.data import ConfigKeys


class Finder:

    def __init__(self):
        self.conf = Config.load(ConfigType.IMPARTUS)
        self.logger = logging.getLogger(self.__class__.__name__)
        pass

    def get_offline_content(self):
        offline_content = dict()
        count = 0
        for dirpath, subdirs, files in os.walk(self.conf.get('target_dir').get(platform.system())):
            for ttid, video_metadata in self.get_offline_video_metadata(dirpath, files):
                if ttid:
                    count += 1
                    backpack_slides = self.get_offline_backpack_slides(dirpath, files)
                    chats = self.get_offline_chats(dirpath, files)
                    offline_content[ttid] = {
                        'backpack_slides': backpack_slides,
                        'chats': chats,
                        **video_metadata,
                    }
        return offline_content

    def get_offline_video_metadata(self, path: str, files: List) -> (str, Dict):
        for filename in files:
            if not filename.endswith('.mkv'):
                continue
            filepath = os.path.join(path, filename)
            ttid = self._get_ttid(filepath)
            if ttid:
                try:
                    metadata_file = '{}/{}.json'.format(
                        self.conf.get(ConfigKeys.CONFIG_DIR.value).get(platform.system()),
                        ttid
                    )
                    video_metadata = dict()
                    if os.path.exists(metadata_file):
                        with open(metadata_file, 'r') as fh:
                            video_metadata = json.load(fh)
                            video_metadata = Utils.add_new_fields(video_metadata)
                    else:
                        # construct from path.
                        video_path_format = self.conf.get(ConfigKeys.VIDEO_PATH.value)
                        placeholders = re.compile(r"{.*?}")
                        matches = placeholders.findall(video_path_format)

                        sep = r"[/\\-]"
                        copy_filepath = filepath

                        # path_components = {}
                        for match in matches:
                            # {target_dir}, {subjectNameShort}, ...
                            video_path_format = video_path_format.replace(match, '')
                            if match == '{target_dir}':
                                pattern = self.conf.get(ConfigKeys.TARGET_DIR.value).get(platform.system())
                            elif match == '{startDate}':
                                pattern = r'[0-9]{4}-[0-9]{2}-[0-9]{2}'
                            elif match == '{ext}':
                                pattern = r'mkv'
                            elif match == '{seqNo}':
                                pattern = r'[0-9]{2}'
                            elif match == '{tapNToggle}':
                                pattern = r'[0-9]'
                            elif match == '{professorName}':
                                pattern = r'[a-zA-Z0-9-]+'
                            else:
                                pattern = r'([a-zA-Z0-9\._-]+)(?=.*-[0-9]{4}-[0-9]{2}-[0-9]{2})'
                            field = match[1:len(match)-1]
                            if re.match(pattern, copy_filepath):
                                video_metadata[field] = re.match(pattern, copy_filepath).group(0)
                            copy_filepath = re.sub(pattern, '', copy_filepath, 1)
                            copy_filepath = re.sub(sep, '', copy_filepath, 1)

                        video_metadata['tapNToggle'] = '?'
                        video_metadata['actualDurationReadable'] = '--:--'
                        video_metadata['ttid'] = ttid
                        video_metadata['ext'] = ''
                        video_metadata['slide_url'] = ''
                        del video_metadata['target_dir']

                    # for all videos...
                    video_metadata['offline_filepath'] = filepath
                    yield ttid, video_metadata

                except NameError as ex:
                    self.logger.warning('config_dir not found, or does not exist. error: {}'.format(ex))
                except SyntaxError as ex:
                    self.logger.warning('error reading metadata file: {}'.format(ex))

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

    def _get_ttid(self, filepath: str):
        try:
            with open(filepath, 'rb') as f:
                mkv = enzyme.MKV(f)
                if mkv.tags:
                    for x in mkv.tags:
                        for y in x.simpletags:
                            if y.name == 'TTID':
                                return int(y.string)
        except enzyme.MalformedMKVError as ex:
            self.logger.warning("Exception while parsing file {}".format(str(filepath)))
            self.logger.warning("You may want to delete and re-download this file.")
            self.logger.warning("Exception: {}".format(ex))
            pass


if __name__ == '__main__':
    conf = Config.load(ConfigType.IMPARTUS)
    con = Finder().get_offline_content()
    print(con)
