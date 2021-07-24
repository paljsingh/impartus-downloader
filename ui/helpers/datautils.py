import os
import platform

import requests

from lib.config import Config, ConfigType
from lib.utils import Utils


class DataUtils:

    @classmethod
    def merge_items(cls, offline_item, online_item):
        for key, val in offline_item.items():
            if not online_item.get(key):
                online_item[key] = offline_item[key]
        return online_item

    @classmethod
    def save_metadata(cls, online_data):
        conf = Config.load(ConfigType.IMPARTUS)
        if conf.get('config_dir') and conf.get('config_dir').get(platform.system()) \
                and conf.get('save_offline_lecture_metadata'):
            folder = conf['config_dir'][platform.system()]
            os.makedirs(folder, exist_ok=True)
            for ttid, item in online_data.items():
                filepath = os.path.join(folder, '{}.json'.format(ttid))
                if not os.path.exists(filepath):
                    Utils.save_json(item, filepath)

    @classmethod
    def get_releases(cls):
        url = 'https://api.github.com/repos/paljsingh/impartus-downloader/releases'
        response = requests.get(url)
        if response.status_code == 200:
            return response.json()
