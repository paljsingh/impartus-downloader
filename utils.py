import os
import re
from typing import Dict, List
from config import Config
import webbrowser
from datetime import datetime


class Utils:

    @classmethod
    def add_fields(cls, metadata, video_slide_mapping):
        conf = Config.load()

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
        metadata['subjectNameShort'] = metadata['subjectName']
        for key, val in conf.get('subject_mapping').items():
            if re.search(key, metadata['subjectName']):
                metadata['subjectNameShort'] = val
                break

        return metadata

    @classmethod
    def sanitize(cls, metadata: Dict):  # noqa
        """
        Sanitize the fields in the metadata item for better display.
        Also creates a few new fields.
        """
        if metadata is None:
            return

        # let the original metadata fields be accessible as field_raw
        # sanitize the fields...
        safe_chars = ['subjectName', 'institute', 'sessionName', 'professorName', 'topic', 'subjectDescription']

        for x in safe_chars:
            # remove leading/trailing spaces, replace other non-alphanum chars with '-'
            # also replace 2 or more consecutive "-" with single "-"

            # save a copy of the original field as field_raw
            metadata['{}_raw'.format(x)] = metadata[x]
            if metadata.get(x):
                metadata[x] = re.sub(r"[-]{2,}", "-", re.sub(r'[^a-zA-Z0-9_-]', '-', str.strip(metadata[x])))

        fixed_width_numeric = {'seqNo': '{:02d}', 'views': '{:04d}', 'actualDuration': '{:05d}', 'sessionId': '{:04d}'}
        for key, val in fixed_width_numeric.items():
            # format these numeric fields to fix width with leading zeros.
            if metadata[key]:
                metadata[key] = val.format(metadata[key])

        return metadata

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
