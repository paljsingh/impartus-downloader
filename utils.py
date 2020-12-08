import os
import re
from enum import Enum
from typing import Dict


class CompareType(Enum):
    EQ = 1
    ENDS_WITH = 2
    STARTS_WITH = 3
    CONTAINS = 4


class Utils:

    @classmethod
    def find_file(cls, name: str, directory: str, comp_type: CompareType):
        for root, subdirs, files in os.walk(directory):
            if comp_type == CompareType.EQ:
                if name in files:
                    return os.path.join(root, name)
            if comp_type == CompareType.ENDS_WITH:
                for file in files:
                    if file.endswith(name):
                        return os.path.join(root, file)
            if comp_type == CompareType.STARTS_WITH:
                for file in files:
                    if file.startswith(name):
                        return os.path.join(root, file)
            if comp_type == CompareType.CONTAINS:
                for file in files:
                    if name in file:
                        return os.path.join(root, file)

    @classmethod
    def find_dir(cls, name: str, directory: str, comp_type: CompareType):
        for root, subdirs, files in os.walk(directory):
            if comp_type == CompareType.EQ:
                if name in subdirs:
                    return os.path.join(root, name)
            if comp_type == CompareType.ENDS_WITH:
                for directory in subdirs:
                    if directory.endswith(name):
                        return os.path.join(root, directory)
            if comp_type == CompareType.STARTS_WITH:
                for directory in subdirs:
                    if directory.startswith(name):
                        return os.path.join(root, directory)
            if comp_type == CompareType.CONTAINS:
                for directory in subdirs:
                    if name in directory:
                        return os.path.join(root, directory)

    @classmethod
    def sanitize(cls, data_dict: Dict):  # noqa
        if data_dict is None:
            return

        strip_spaces = ['subjectName', 'institute', 'sessionName', 'professorName', 'topic', 'subjectDescription']
        date_extract = ['startTime', 'endTime']
        fixed_width = {'seqNo': '{:02d}', 'views': '{:04d}', 'actualDuration': '{:05d}', 'sessionId': '{:04d}'}

        for x in strip_spaces:
            # remove leading/trailing spaces, replace other non-alphanum chars with '-'
            if data_dict[x]:
                data_dict[x] = re.sub(r'[^a-zA-Z0-9_/-]', '-', str.strip(data_dict[x]))

        for x in date_extract:
            # extract date field
            if data_dict[x]:
                data_dict[x] = str.split(data_dict[x], ' ')[0]

        for key, val in fixed_width.items():
            # remove leading/trailing spaces, replace other non-alphanum chars with '-'
            if data_dict[key]:
                data_dict[key] = val.format(data_dict[key])

        return data_dict


if __name__ == '__main__':
    print(Utils.find_dir(
        "impartus",
        os.path.join(os.environ.get('HOME'), "Library/Application Support/Firefox/Profiles"),
        CompareType.CONTAINS
    ))

    print(Utils.find_file(
        "webappsstore.sqlite",
        os.path.join(os.environ.get('HOME'), "Library/Application Support/Firefox/Profiles"),
        CompareType.EQ
    ))