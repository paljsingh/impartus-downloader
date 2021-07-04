import json
import logging
import os
import platform
import re
import shutil
import subprocess
from typing import List
import webbrowser
from datetime import datetime

from lib.config import Config, ConfigType
from ui.data.columns import Columns


class Utils:
    """
    Utility functions.
    """

    @classmethod
    def add_new_fields(cls, metadata):
        try:
            # pad the following fields
            fixed_width_numeric = {
                'seqNo': '{:02d}', 'views': '{:04d}', 'actualDuration': '{:05d}', 'sessionId': '{:04d}'
            }
            for key, val in fixed_width_numeric.items():
                # format these numeric fields to fix width with leading zeros.
                if metadata[key] is not None:
                    metadata[key] = val.format(int(metadata[key]))

            date_fields = {'startTime': 'startDate', 'endTime': 'endDate'}
            for key, val in date_fields.items():
                # extract datetime fields, and create new fields named startDate, endDate
                if metadata[key]:
                    metadata[val] = str.split(metadata[key], ' ')[0]
            # create new field to show human readable duration of the video.
            duration_hour = int(metadata.get('actualDuration')) // 3600
            duration_min = (int(metadata.get('actualDuration')) % 3600) // 60
            metadata['actualDurationReadable'] = '{}:{:02d}h'.format(duration_hour, duration_min)

            # We may want to display a shorter subject name, or a shorter faculty name (or any other field..)
            # This is indicated by the presence of 'original_col_name' field in Columns.data_columns
            col_mapping = {k: v['original_values_col'] for k, v in Columns.data_columns.items()
                           if v.get('original_values_col')}

            # for all such columns, load (if any) mappings exist in etc/mappings.conf
            mappings_conf = Config.load(ConfigType.MAPPINGS)
            for new_col_name, orig_col_name in col_mapping.items():

                metadata[new_col_name] = metadata[orig_col_name]  # default, if we can't find a mapping.

                if mappings_conf.get(new_col_name):
                    for mapping_key, mapping_val in mappings_conf[new_col_name].items():

                        # create a new field in the metadata with the mapping value
                        # e.g. metadata['subjectMameShort'] = 'ML'
                        # where there exists another field: metadata['subjectName'] == 'DSE_SEC-1-MACHINE-LEARNING'
                        if metadata[orig_col_name] == mapping_key:
                            metadata[new_col_name] = mapping_val
                            break
        except KeyError as ex:
            logger = logging.getLogger(cls.__name__)
            logger.warning('Error parsing lecture metadata - {}'.format(ex))

        return metadata

    @classmethod
    def sanitize(cls, path: str):  # noqa
        """
        Sanitize the given path for storage.
        """

        path = re.sub(r'[^\\0-9a-zA-Z/:_.]', '-', path)         # replace all bad chars with '-'
        path = re.sub(r"[^a-zA-Z0-9/\\]{2,}", '-', path)        # replace consecutive non-alphanum with single '-'
        path = re.sub(r"^(.*)[^a-zA-Z0-9]+$", r'\1', path)      # strip bad chars at end
        path = re.sub(r"^[^a-zA-Z0-9/]+(.*)$", r'\1', path)     # strip bad chars at beginning
        path = re.sub(r'([/\\])[^a-zA-Z0-9:]+', r'\1', path)     # strip bad chars after '/' or '\'
        path = re.sub(r"[^a-zA-Z0-9:]+([/\\])", r'\1', path)     # strip bad chars before '/' or '\'
        return path

    @classmethod
    def delete_files(cls, files: List):
        for file in files:
            os.unlink(file)

    @classmethod
    def get_temp_dir(cls):
        for env_var in ['TMPDIR', 'TEMP', 'TMP']:
            if os.environ.get(env_var):
                return os.environ.get(env_var)
        for tmp_path in ['/tmp', '/var/tmp', 'c:\\windows\\temp']:
            if os.path.exists(tmp_path):
                return tmp_path

    @classmethod
    def open_file(cls, path, event=None):   # noqa
        if re.match('https?', path) or re.match('file:', path):
            webbrowser.open(r'{}'.format(path))
        elif platform.system() == 'Darwin':
            # when preview.app, keynote.app is already launched,
            # a second window often throws an error: 'cannot import <file>'
            # use 'open' launcher.
            subprocess.run(["open", path])
        else:
            webbrowser.open(r'file://{}'.format(path))

    @classmethod
    def date_difference(cls, date1, date2):
        date_format = "%Y-%m-%d"
        delta = datetime.strptime(date1, date_format) - datetime.strptime(date2, date_format)
        return delta.days

    @classmethod
    def move_and_rename_file(cls, source, destination):
        if source != destination:
            os.makedirs(os.path.dirname(destination), exist_ok=True)
            shutil.move(source, destination)

    @classmethod
    def save_json(cls, content, filepath):
        with open(filepath, "w") as fh:
            json.dump(content, fh, indent=4)
