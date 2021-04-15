import os
import re
import yaml
from typing import Dict, List
from config import Config
import webbrowser
from datetime import datetime


class Utils:

    @classmethod
    def add_new_fields(cls, metadata, video_slide_mapping):
        conf = Config.load('impartus.conf')

        metadata['ext'] = None
        slides = video_slide_mapping.get(metadata['ttid'])
        if slides:
            ext = video_slide_mapping.get(metadata['ttid']).split('.')[-1].lower()
            if ext in conf.get('allowed_ext'):
                metadata['ext'] = ext

        date_fields = {'startTime': 'startDate', 'endTime': 'endDate'}
        for key, val in date_fields.items():
            # extract datetime fields, and create new fields named startDate, endDate
            if metadata[key]:
                metadata[val] = str.split(metadata[key], ' ')[0]

        # create new field to show human readable duration of the video.
        duration_hour = int(metadata.get('actualDuration')) // 3600
        duration_min = (int(metadata.get('actualDuration')) % 3600) // 60
        metadata['actualDurationReadable'] = '{}:{:02d}h'.format(duration_hour, duration_min)

        # create new field to hold shortened subject names.
        mapping_item = 'subjectName'
        metadata['subjectNameShort'] = metadata[mapping_item]
        conf_subject = Config.load('mappings.conf')
        if conf_subject.get(mapping_item):
            for key, val in conf_subject.get(mapping_item).items():
                # escape posix special chars
                key = re.escape(key)
                if re.search(key, metadata[mapping_item]):
                    metadata['subjectNameShort'] = val
                    break

        return metadata

    @classmethod
    def sanitize(cls, path: str):  # noqa
        """
        Sanitize the fields in the metadata item for better display.
        Also creates a few new fields.
        """
        path = re.sub(r'[^\\0-9a-zA-Z/:_.]', '-', path)
        path = re.sub(r"[-]{2,}", "-", path)
        path = re.sub(r"[^0-9a-zA-Z]+([/\\])", r'\1', path)
        return path

    @classmethod
    def delete_files(cls, files: List):
        for file in files:
            os.unlink(file)

    @classmethod
    def get_temp_dir(cls):
        if os.environ.get('TMPDIR'):
            return os.environ.get('TMPDIR')
        if os.environ.get('TEMP'):
            return os.environ.get('TEMP')
        if os.environ.get('TMP'):
            return os.environ.get('TMP')
        return '/tmp'

    @classmethod
    def open_file(cls, path):
        webbrowser.open('file://{}'.format(path))

    @classmethod
    def date_difference(cls, date1, date2):
        date_format = "%Y-%m-%d"
        delta = datetime.strptime(date1, date_format) - datetime.strptime(date2, date_format)
        return delta.days

    @classmethod
    def write_config(cls, config, file):
        with open(file, 'w') as outfile:
            yaml.dump(config, outfile, default_flow_style=False, default_style="'")
