import os
import re
from enum import Enum
from typing import Dict, List


class CompareType(Enum):
    EQ = 1
    ENDS_WITH = 2
    STARTS_WITH = 3
    CONTAINS = 4


class Utils:

    @classmethod
    def find_files(cls, name: str, directory: str, comp_type: CompareType):
        files_list = []
        for root, subdirs, files in os.walk(directory):
            if comp_type == CompareType.EQ:
                if name in files:
                    files_list.append(os.path.join(root, name))
            if comp_type == CompareType.ENDS_WITH:
                for file in files:
                    if file.endswith(name):
                        files_list.append(os.path.join(root, file))
            if comp_type == CompareType.STARTS_WITH:
                for file in files:
                    if file.startswith(name):
                        files_list.append(os.path.join(root, file))
            if comp_type == CompareType.CONTAINS:
                for file in files:
                    if name in file:
                        files_list.append(os.path.join(root, file))
        return files_list

    @classmethod
    def find_dirs(cls, name: str, directory: str, comp_type: CompareType):
        """
        Find directories matching a given string and comparison type.

        """
        dirs_list = []
        for root, subdirs, files in os.walk(directory):
            if comp_type == CompareType.EQ:
                if name in subdirs:
                    dirs_list.append(os.path.join(root, name))
            if comp_type == CompareType.ENDS_WITH:
                for directory in subdirs:
                    if directory.endswith(name):
                        dirs_list.append(os.path.join(root, directory))
            if comp_type == CompareType.STARTS_WITH:
                for directory in subdirs:
                    if directory.startswith(name):
                        dirs_list.append(os.path.join(root, directory))
            if comp_type == CompareType.CONTAINS:
                for directory in subdirs:
                    if name in directory:
                        dirs_list.append(os.path.join(root, directory))
        return dirs_list

    @classmethod
    def sanitize(cls, metadata: Dict):  # noqa
        """
        Sanitize the fields in the metadata item, for better display.
        Also creates a few new fields.
        """
        if metadata is None:
            return

        strip_spaces = ['subjectName', 'institute', 'sessionName', 'professorName', 'topic', 'subjectDescription']
        datetime_fields = {'startTime': 'startDate', 'endTime': 'endDate'}
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
            # remove leading/trailing spaces, replace other non-alphanum chars with '-'
            if metadata[key]:
                metadata[key] = val.format(metadata[key])

        return metadata

    @classmethod
    def read_file(cls, filepath: str):
        """
        extract encryption key from the key-file.
        :param filepath:
        :return:
        """
        with open(filepath, 'rb') as fh:
            content = fh.read()
        return content

    @classmethod
    def delete_files(cls, files: List):
        for file in files:
            os.unlink(file)
