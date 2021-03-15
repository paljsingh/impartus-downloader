import os
import re
from typing import Dict, List
from config import Config
import webbrowser
from datetime import datetime


class Utils:

    @classmethod
    def sanitize(cls, metadata: Dict):  # noqa
        """
        Sanitize the fields in the metadata item for better display.
        Also creates a few new fields.
        """
        if metadata is None:
            return

        strip_spaces = ['subjectName', 'institute', 'sessionName', 'professorName', 'topic', 'subjectDescription']
        datetime_fields = {
            'startTime': 'startDate',
            'endTime': 'endDate'
        }
        fixed_width = {'seqNo': '{:02d}', 'views': '{:04d}', 'actualDuration': '{:05d}', 'sessionId': '{:04d}'}

        for x in strip_spaces:
            # remove leading/trailing spaces, replace other non-alphanum chars with '-'
            # also replace 2 or more consecutive "-" with single "-"
            if metadata[x]:
                metadata[x] = re.sub(r"[-]{2,}", "-", re.sub(r'[^a-zA-Z0-9_/-]', '-', str.strip(metadata[x])))

        for key, val in datetime_fields.items():
            # extract datetime fields, and create new fields named startDate, endDate
            if metadata[key]:
                metadata[val] = str.split(metadata[key], ' ')[0]

        for key, val in fixed_width.items():
            # format these numeric fields to fix width with leading zeros.
            if metadata[key]:
                metadata[key] = val.format(metadata[key])

        # create new field to hold shortened subject names.
        conf = Config.load()
        for key, val in conf.get('subject_mapping').items():
            if re.search(key, metadata['subjectName']):
                metadata['subjectNameShort'] = val
                break

        # create new field to show human readable duration of the video.
        duration_hour = int(metadata.get('actualDuration')) // 3600
        duration_min = (int(metadata.get('actualDuration')) % 3600) // 60
        metadata['actualDurationReadable'] = '{}h{}m'.format(duration_hour, duration_min)
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


