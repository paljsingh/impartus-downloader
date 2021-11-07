import json
import os
import platform
import re
import shutil
import subprocess
import sys
from typing import List
import webbrowser
from datetime import datetime

from lib.config import Config, ConfigType
from lib.metadataparser import MetadataDictParser
from lib.data.labels import ConfigKeys


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
            # for Mac, use 'open' launcher to open non-web urls.
            # 'webbrowser' launcher throws error 'cannot import <file>' when preview.app, keynote.app
            # is already open.
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
        with open(filepath, "w", encoding="utf-8") as fh:
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
    def get_filepath(cls, metadata, config_key: str):
        conf = cls.conf
        download_dir = conf.get(ConfigKeys.TARGET_DIR.value).get(platform.system())
        if conf.get(ConfigKeys.USE_SAFE_PATHS.value):
            sanitized_components = MetadataDictParser.sanitize(MetadataDictParser.parse_metadata(metadata))
            file_path = conf.get(config_key).format(
                **{**metadata, **sanitized_components}, target_dir=download_dir
            )
        else:
            file_path = conf.get(config_key).format(**metadata, target_dir=download_dir)
        return file_path

    @staticmethod
    def get_mkv_path(video_metadata):
        return Utils.get_filepath(video_metadata, ConfigKeys.VIDEO_PATH.value)

    @staticmethod
    def get_documents_path(metadata):
        return Utils.get_filepath(metadata, ConfigKeys.DOCUMENTS_PATH.value)

    @staticmethod
    def get_captions_path(video_metadata):
        return Utils.get_filepath(video_metadata, ConfigKeys.CAPTIONS_PATH.value)

    @classmethod
    def slides_exist_on_disk(cls, path):
        conf = cls.conf
        path_without_ext = path.rsplit('.', 1)[0]
        for ext in conf.get(ConfigKeys.ALLOWED_EXT.value):
            path_with_ext = '{}.{}'.format(path_without_ext, ext)
            if os.path.exists(path_with_ext):
                return True, path_with_ext
        return False, path

        #
        # except AttributeError:
        #     if level < -13:
        #         process.nice(psutil.REALTIME_PRIORITY_CLASS)
        #     elif -13 <= level < -7:
        #         process.nice(psutil.HIGH_PRIORITY_CLASS)
        #     elif -7 <= level < 0:
        #         process.nice(psutil.ABOVE_NORMAL_PRIORITY_CLASS)
        #     elif 0 <= level < 7:
        #         process.nice(psutil.NORMAL_PRIORITY_CLASS)
        #     elif 7 <= level < 12:
        #         process.nice(psutil.BELOW_NORMAL_PRIORITY_CLASS)
        #     elif 13 <= level:
        #         process.nice(psutil.IDLE_PRIORITY_CLASS)

    @classmethod
    def run_with_priority(cls, command: str, priority='normal'):
        command_args = command.split(' ')
        if sys.platform == 'Windows':
            priorities = {
                'normal': subprocess.NORMAL_PRIORITY_CLASS,
                'low': subprocess.BELOW_NORMAL_PRIORITY_CLASS,
                'lowest': subprocess.IDLE_PRIORITY_CLASS
            }
            priority_class = priorities[priority] if priorities.get(priority) else subprocess.NORMAL_PRIORITY_CLASS
            process = subprocess.Popen(command_args, creationFlags=priority_class)
        else:
            nice_values = {
                'normal': 0,
                'low': 10,
                'lowest': 20,
            }
            nice_value = nice_values[priority] if nice_values.get(priority) else 0
            process = subprocess.Popen(command_args, preexec_fn=lambda: os.nice(nice_value))
        return process.wait()
