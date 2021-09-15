import json
import os
import platform
import re
import shutil
import subprocess
from typing import List
import webbrowser
from datetime import datetime

from lib.config import Config, ConfigType
from lib.metadataparser import MetadataDictParser
from lib.data.configkeys import ConfigKeys
from ui.helpers.datautils import DataUtils


class Utils:
    """
    Utility functions.
    """
    conf = Config.load(ConfigType.IMPARTUS)

    @staticmethod
    def delete_files(files: List):
        for file in files:
            os.unlink(file)

    @staticmethod
    def get_temp_dir():
        for env_var in ['TMPDIR', 'TEMP', 'TMP']:
            if os.environ.get(env_var):
                return os.environ.get(env_var)
        for tmp_path in ['/tmp', '/var/tmp', 'c:\\windows\\temp']:
            if os.path.exists(tmp_path):
                return tmp_path

    @staticmethod
    def open_file(path, event=None):   # noqa
        if re.match('https?', path) or re.match('file:', path):
            webbrowser.open(r'{}'.format(path))
        elif platform.system() == 'Darwin':
            # when preview.app, keynote.app is already launched,
            # a second window often throws an error: 'cannot import <file>'
            # use 'open' launcher.
            subprocess.run(["open", path])
        else:
            webbrowser.open(r'file://{}'.format(path))

    @staticmethod
    def date_difference(date1, date2):
        date_format = "%Y-%m-%d"
        delta = datetime.strptime(date1, date_format) - datetime.strptime(date2, date_format)
        return delta.days

    @staticmethod
    def move_and_rename_file(source, destination):
        if source != destination:
            os.makedirs(os.path.dirname(destination), exist_ok=True)
            shutil.move(source, destination)

    @staticmethod
    def save_json(content, filepath):
        with open(filepath, "w") as fh:
            json.dump(content, fh, indent=4)

    @staticmethod
    def get_url_for_highest_quality_video(conf, m3u8_urls):
        for resolution in conf.get(ConfigKeys.FLIPPED_LECTURE_QUALITY_ORDER.value):
            for url in m3u8_urls:
                if resolution in url:
                    return url

    @staticmethod
    def get_url_for_lowest_quality_video(conf, m3u8_urls):
        for resolution in reversed(conf.get(ConfigKeys.FLIPPED_LECTURE_QUALITY_ORDER.value)):
            for url in m3u8_urls:
                if resolution in url:
                    return url

    @staticmethod
    def get_url_for_resolution(m3u8_urls, resolution):
        for url in m3u8_urls:
            if resolution in url:
                return url

    @classmethod
    def get_filepath(cls, video_metadata, config_key: str):
        conf = cls.__class__.conf
        download_dir = conf.get(ConfigKeys.TARGET_DIR.value)
        if conf.get(ConfigKeys.USE_SAFE_PATHS.value):
            sanitized_components = MetadataDictParser.sanitize(MetadataDictParser.parse_metadata(video_metadata))
            file_path = conf.get(config_key).format(
                **{**video_metadata, **sanitized_components}, target_dir=download_dir
            )
        else:
            file_path = conf.get(config_key).format(**video_metadata, target_dir=download_dir)
        return file_path

    @staticmethod
    def get_mkv_path(video_metadata):
        return Utils.get_filepath(video_metadata, ConfigKeys.VIDEO_PATH.value)

    @staticmethod
    def get_slides_path(video_metadata):
        return Utils.get_filepath(video_metadata, ConfigKeys.SLIDES_PATH.value)

    @staticmethod
    def get_captions_path(video_metadata):
        return Utils.get_filepath(video_metadata, ConfigKeys.CAPTIONS_PATH.value)

    @classmethod
    def slides_exist_on_disk(cls, path):
        conf = cls.__class__.conf
        path_without_ext = path.rsplit('.', 1)[0]
        for ext in conf.get(ConfigKeys.ALLOWED_EXT.value):
            path_with_ext = '{}.{}'.format(path_without_ext, ext)
            if os.path.exists(path_with_ext):
                return True, path_with_ext
        return False, path

    @staticmethod
    def get_subject_mappings(subjects):
        mapping_by_id = dict()
        mapping_by_name = dict()
        for subject_metadata in subjects:
            mapping_by_id[subject_metadata['subjectId']] = subject_metadata
            mapping_by_name[subject_metadata['subjectName']] = subject_metadata
        return mapping_by_id, mapping_by_name

    @staticmethod
    def subject_id_to_subject_name(slides_metadata, mappings_by_id):
        new_metadata_dict = dict()
        for subject_id, val in slides_metadata.items():
            subject_name = mappings_by_id[subject_id].get('subjectName')
            new_key = DataUtils.get_subject_name_short_from_subject_name(subject_name)
            new_metadata_dict[new_key] = val
        return new_metadata_dict

