import os
import platform
import re
from typing import Dict, List

from lib.config import Config, ConfigType
from lib.data.columns import Columns
from lib.threadlogging import ThreadLogger


class MetadataDictParser:

    thread_logger = ThreadLogger(__name__).logger

    fields = {
        "trending": {
            'datatype': int,    # - int, str, float .. ?
            'regex': r'[0-9]',  # - regex to match this field in a filepath.
            'priority': 10,     # - when file path has multiple fields in the same path component,
                                #   e.g. $root_path/{subjectName}-{seqNo}-{startDate}/...
                                #   one with higher priority shall be tried for a match first.
                                #   simpler, restrictive regex are given higher priority (towards 10), while
                                #   loose/match-all regexes have priority value towards 1. (on a scale 1-10 )
            'default': 0,       # - default value for this field, if cannot be obtained from filepath.
        },
        "type": {
            'datatype': int,
            'regex': r'[0-9]',
            'priority': 10,
            'default': 0,
        },
        "lessonPlanAvailable": {
            'datatype': int,
            'regex': r'[0-9]',
            'priority': 10,
            'default': 0,
        },
        "ttid": {
            'datatype': int,
            'regex': r'[0-9]+',
            'priority': 8,
            'default': None,    # must be present.
        },
        "seqNo": {
            'datatype': str,
            'regex': r'[0-9]{1,2}',
            'priority': 9,
            'default': '01',
        },
        "status": {
            'datatype': int,
            'regex': r'-?[0-9]',
            'priority': 9,
            'default': 0,
        },
        "videoId": {
            'datatype': int,
            'regex': r'[0-9]+',
            'priority': 8,
            'default': 0,
        },
        "subjectId": {
            'datatype': int,
            'regex': r'[0-9]+',
            'priority': 8,
            'default': 0,
        },
        "subjectName": {
            'datatype': str,
            'regex': r'[^/\\]+',
            'priority': 2,
            'default': '-',
            'sanitize': True,
        },
        "subjectNameShort": {
            'datatype': str,
            'regex': r'[^/\\]+',
            'priority': 2,
            'default': 'Misc',
            'sanitize': True,
        },
        "safeenroll": {
            'datatype': int,
            'regex': r'[0-9]',
            'priority': 10,
            'default': 0,
        },
        "coverpic": {
            'datatype': str,
            'regex': r'/[a-zA-Z0-9/\._-]+',
            'priority': 1,
            'default': '-',
            'sanitize': True,
        },
        "subjectCode": {
            'datatype': str,
            'regex': r'[a-zA-Z0-9_-]+',
            'priority': 3,
            'default': '-',
            'sanitize': True,
        },
        "subjectDescription": {
            'datatype': str,
            'regex': r'[^/\\]+',
            'priority': 2,
            'default': '-',
            'sanitize': True,
        },
        "instituteId": {
            'datatype': int,
            'regex': r'[0-9]+',
            'priority': 8,
            'default': 0,
        },
        "institute": {
            'datatype': str,
            'regex': r'[^/\\]+',
            'priority': 2,
            'default': '-',
            'sanitize': True,
        },
        "departmentId": {
            'datatype': int,
            'regex': r'[0-9]+',
            'priority': 8,
            'default': 0,
        },
        "department": {
            'datatype': str,
            'regex': r'[^/\\]+',
            'priority': 2,
            'default': '-',
            'sanitize': True,
        },
        "classroomId": {
            'datatype': int,
            'regex': r'[0-9]+',
            'priority': 8,
            'default': 0,
        },
        "classroomName": {
            'datatype': str,
            'regex': r'[^/\\]+',
            'priority': 2,
            'default': '-',
            'sanitize': True,
        },
        "sessionId": {
            'datatype': int,
            'regex': r'[0-9]+',
            'priority': 8,
            'default': 0,
        },
        "sessionName": {
            'datatype': str,
            'regex': r'[^/\\]+',
            'priority': 2,
            'default': '-',
            'sanitize': True,
        },
        "topic": {
            'datatype': str,
            'regex': r'[^/\\]+',
            'priority': 2,
            'default': '-',
            'sanitize': True,
        },
        "professorId": {
            'datatype': int,
            'regex': r'[0-9]+',
            'priority': 8,
            'default': 0,
        },
        "professorName": {
            'datatype': str,
            'regex': r'[^/\\]+',
            'priority': 2,
            'default': '-',
            'sanitize': True,
        },
        "professorImageUrl": {
            'datatype': str,
            'regex': r'/[a-zA-Z0-9/\._-]+',
            'priority': 1,
            'default': '-',
            'sanitize': True,
        },
        "startTime": {
            'datatype': str,
            'regex': r'[0-9]{4}-[0-9]{2}-[0-9]{2} [0-9]{2}:[0-9]{2}:[0-9]{2}',
            'priority': 10,
            'default': '1970-01-01 00:00:00',
        },
        "endTime": {
            'datatype': str,
            'regex': r'[0-9]{4}-[0-9]{2}-[0-9]{2} [0-9]{2}:[0-9]{2}:[0-9]{2}',
            'priority': 10,
            'default': '1970-01-01 00:00:00',
        },
        "startDate": {
            'datatype': str,
            'regex': r'[0-9]{4}-[0-9]{2}-[0-9]{2}',
            'priority': 10,
            'default': '1970-01-01',
        },
        "endDate": {
            'datatype': str,
            'regex': r'[0-9]{4}-[0-9]{2}-[0-9]{2}',
            'priority': 10,
            'default': '1970-01-01',
        },
        "actualDuration": {
            'datatype': int,
            'regex': r'[0-9]+',
            'priority': 8,
            'default': 0,
        },
        "actualDurationReadable": {
            'datatype': str,
            'regex': r'[0-9]:[0-9]{2}h',
            'priority': 10,
            'default': '--:--',     # mark it unknown, figure out if it can be extracted from the video.
        },
        "tapNToggle": {
            'datatype': int,
            'regex': r'[0-9]',
            'priority': 10,
            'default': 1,           # may be correct for most cases, figure out how to extract it from the video.
        },
        "filePath": {
            'datatype': str,
            'regex': r'[a-zA-Z0-9/\._:-]+',
            'priority': 2,
            'default': '-',
            'sanitize': True,
        },
        "filePath2": {
            'datatype': str,
            'regex': r'[a-zA-Z0-9/\._:-]+',
            'priority': 2,
            'default': '-',
            'sanitize': True,
        },
        "slideCount": {
            'datatype': int,
            'regex': r'[0-9]+',
            'priority': 9,
            'default': 0,
        },
        "noaudio": {
            'datatype': int,
            'regex': r'[0-9]',
            'priority': 10,
            'default': 0,
        },
        "averageRating": {
            'datatype': float,
            'regex': r'[0-9]\.[0-9]{2}',
            'priority': 10,
            'default': 0.00,
        },
        "views": {
            'datatype': int,
            'regex': r'[0-9]+',
            'priority': 9,
            'default': 0,
        },
        "documentCount": {
            'datatype': int,
            'regex': r'[0-9]+',
            'priority': 9,
            'default': 0,
        },
        "lastPosition": {
            'datatype': int,
            'regex': r'[0-9]+',
            'priority': 9,
            'default': 0,
        },
        "downloaded": {
            'datatype': bool,
            'regex': r'(True|False)',
            'priority': 10,
            'default': True,
        },
        "downloading": {
            'datatype': bool,
            'regex': r'(True|False)',
            'priority': 10,
            'default': False,
        },
        "downloadStatus": {
            'datatype': int,
            'regex': r'[0-9]{,3}',
            'priority': 9,
            'default': 100,
        },
        "m3u8Path": {
            'datatype': str,
            'regex': r'[a-zA-Z0-9/\._:-]+',
            'priority': 2,
            'default': '-',
            'sanitize': True,
        },
        "ext": {    # this is the slides doc extension, rename the field for readability.
            'datatype': str,
            'regex': r'[a-z0-9]{,5}',
            'priority': 6,
            'default': 'pdf',
        },
    }

    @classmethod
    def parse_kv(cls, key, value):
        """
        Parse a given fields[key] pattern against a given value.
        Returns true on success.
        """

        if key in MetadataDictParser.fields.keys():
            field_value = MetadataDictParser.fields[key]
            try:
                if type(value) == field_value['datatype']:
                    pattern = re.compile(field_value['regex'])
                    match = re.search(pattern, value)
                    if match:
                        return True, match.group(0), str.replace(value, match.group(0), '', 1)
            except (KeyError, SyntaxError, NameError, TypeError):
                # ignore these silently.
                pass

        # return NoMatch, match_str: None, remaining_str: same-as-original
        return None, None, value

    @classmethod
    def parse_metadata(cls, metadata: Dict) -> Dict:
        """
        Parse a dict against known key field patterns.
        Returns the matched fields.
        """

        parsed_items = {}
        for key, value in metadata.items():
            flag, _, _ = MetadataDictParser.parse_kv(key, value)
            if flag:
                parsed_items[key] = value

        return parsed_items

    @classmethod
    def sanitize(cls, kv_pair: Dict, suffix='', prefix='', inplace=False) -> Dict:
        """
        Sanitize a given list of values, return a new dict containing the sanitized key values.
        If 'prefix' or 'suffix' string is given, keys in output dict will have the prefix and/or the suffix add to them.
        If inplace is True, the original dict will be modified to have updated values (if no prefix/suffix given)
        or include new values with prefix/suffix strings.
        """
        sanitized_items = {}

        filters = [
            {'pattern': r'[^0-9a-zA-Z_.]', 'replacement': '-'},       # replace all bad chars with '-'
            {'pattern': r'[^a-zA-Z0-9]{2,}', 'replacement': '-'},     # replace consecutive non-alphanum with single '-'
            {'pattern': r'^(.*)[^a-zA-Z0-9]+$', 'replacement': r'\1'},     # strip bad chars at end
            {'pattern': r'^[^a-zA-Z0-9]+(.*)$', 'replacement': r'\1'},     # strip bad chars at beginning
        ]
        for key, value in kv_pair.items():
            if MetadataDictParser.fields.get(key) and MetadataDictParser.fields.get(key).get('sanitize'):
                sanitized_value = value
                for p_filter in filters:
                    pattern = re.compile(p_filter['pattern'])
                    sanitized_value = re.sub(pattern, p_filter['replacement'], sanitized_value)

                if sanitized_value:
                    new_key = '{}{}{}'.format(prefix, key, suffix)
                    sanitized_items[new_key] = sanitized_value

        if inplace:
            for key, value in sanitized_items.items():
                kv_pair[key] = value
            return kv_pair
        else:
            return sanitized_items

    @classmethod
    def add_new_fields(cls, metadata):

        # fill in the missing fields.
        for key, value in MetadataDictParser.fields.items():
            if not metadata.get(key):
                metadata[key] = value['default']

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
            col_mapping = {k: v['original_values_col'] for k, v in Columns.get_video_columns().items()
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
            logger = MetadataDictParser.thread_logger
            logger.warning('Error parsing video metadata - {}'.format(ex))

        return metadata


class MetadataFileParser:

    @classmethod
    def match_placeholders(cls, placeholder_groups: List, values: List) -> Dict:
        """
        Parse a set of strings against expected placeholder keys, using the regex from the known patterns.
        Returns the matched fields.
        """
        parsed_items = {}
        for placeholder_items in placeholder_groups:

            # slice the fields dict for placeholder_items keys
            dict_slice = {k: MetadataDictParser.fields[k] for k in placeholder_items
                          if k in MetadataDictParser.fields.keys()}
            # sort the dict_slice by priority
            placeholder_items_by_priority = sorted(
                dict_slice.items(), key=lambda item: item[1]['priority'], reverse=True)
            for placeholder in placeholder_items_by_priority:
                if not values:
                    break
                value = values.pop(0)

                # As we have split the fields by path separators, any separators showing up in subject/topic fields
                # will span more than 1 list items... iterate over all of them till we find the expected match
                count = 0
                max_tries = 3
                joined_remain_value = ''
                while True:
                    flag, match_value, remain_value = MetadataDictParser.parse_kv(placeholder[0], value)
                    if remain_value:
                        joined_remain_value = '{}{}'.format(joined_remain_value, remain_value)

                    if match_value or count >= max_tries or not values:
                        break

                    # take the next value, join it with the current remaining to parse.
                    value = '{}-{}'.format(joined_remain_value, values.pop(0))
                    count += 1

                if joined_remain_value:
                    values.insert(0, joined_remain_value)
                if flag:
                    parsed_items[placeholder[0]] = match_value
        return parsed_items

    @classmethod
    def parse_from_filepath(cls, filepath: str, path_config: str):
        # construct from path.
        conf = Config.load(ConfigType.IMPARTUS)
        target_dir = conf.get('target_dir')[platform.system()]
        path_pattern = re.compile(r"[/\\]+")

        # remove target_dir, ext placeholders.
        path_format = conf.get(path_config)
        path_format = str.replace(path_format, '{target_dir}/', '', 1)  # remove target_dir
        path_format = path_format.rsplit('.', 1)[0]                     # remove extension.

        # split placeholders path format by separator first,
        # so that we have a list that looks like the following:
        # ['{subjectName}', '{professorName}', '{seqNo}', '{topic}-{date}'...]
        placeholder_item_groups = re.split(path_pattern, path_format)

        # now split the placeholder groups, and extract the placeholders key, (still in groups)
        # resulting list should have the format:
        # [['subjectName'], ['professorName'], ['seqNo'], ['topic', 'date'], ... ]
        placeholders_pattern = re.compile(r"{(.*?)}")
        placeholders = list()
        for placeholder_group in placeholder_item_groups:
            placeholders.append(re.findall(placeholders_pattern, placeholder_group))

        relative_path = os.path.relpath(filepath, target_dir)
        relative_path = relative_path.rsplit('.', 1)[0]  # remove extension

        # collect path items for metadata -
        path_items = re.split(path_pattern, relative_path)

        parsed_items = MetadataFileParser.match_placeholders(placeholders, path_items)
        return parsed_items
