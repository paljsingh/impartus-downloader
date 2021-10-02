import os
import platform
from collections import defaultdict

import requests

from lib.config import Config, ConfigType
from lib.metadataparser import MetadataDictParser
from lib.utils import Utils


class DataUtils:

    @classmethod
    def merge_items(cls, offline_items, online_items):
        merged_items = dict()
        for key, val in offline_items.items():
            if online_items.get(key):
                # consider online info, it may have updated topic/metadata not available offline.
                merged_items[key] = online_items[key]
            else:
                merged_items[key] = offline_items[key]
        return merged_items

    @classmethod
    def merge_slides_items(cls, offline_items, online_items, mapping_by_id):
        all_docs = dict()
        if online_items:
            for subject, documents in online_items.items():
                for document in documents:
                    all_docs[document['fileName']] = document

        if offline_items:
            for subject, documents in offline_items.items():
                for document in documents:
                    if not all_docs.get(document['fileName']):
                        all_docs[document['fileName']] = document

        merged_docs_by_subject = defaultdict(list)
        for filename, doc in all_docs.items():
            doc = MetadataDictParser.add_new_fields(doc)
            subject_id = doc['subjectId']
            if mapping_by_id.get(subject_id) and mapping_by_id[subject_id].get('subjectName'):
                key = mapping_by_id[subject_id]['subjectName']
                merged_docs_by_subject[key].append(doc)
            else:
                name = doc['subjectNameShort'] if doc.get('subjectNameShort') else doc.get('subjectName')
                merged_docs_by_subject[name].append(doc)

        return merged_docs_by_subject

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

    @classmethod
    def get_subject_name_from_subject_name_short(cls, short_name):
        conf = Config.load(ConfigType.MAPPINGS)
        for key, val in conf.items():
            if val == short_name:
                return key
        return short_name

    @classmethod
    def get_subject_name_short_from_subject_name(cls, subject_name):
        conf = Config.load(ConfigType.MAPPINGS)
        if conf.get(subject_name):
            return conf.get(subject_name)
        else:
            return subject_name

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
