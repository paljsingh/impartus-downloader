import pytest
from mock import call


def test_move_and_rename_file(mocker):
    mocker.patch('os.makedirs')
    mocker.patch('os.path.dirname')
    mock_move = mocker.patch('shutil.move')

    from lib.utils import Utils

    source = '/tmp/1'
    dest = '/tmp/2'
    Utils.move_and_rename_file(source, dest)
    assert mock_move.call_count == 1
    mock_move.assert_called_once_with(source, dest)
    mock_move.reset_mock()

    # no shutil.move call when source and destination are same.
    Utils.move_and_rename_file(source, source)
    assert mock_move.call_count == 0


def test_date_difference():
    from lib.utils import Utils

    date1 = '2020-01-31'
    date2 = '2020-01-01'
    assert Utils.date_difference(date1, date2) == 30

    # bad dates
    bad_dates = ['2020-02-00', '2020-02-30', '2021-02-29', '02-01-2021', '2021-13-11']
    for bad_date in bad_dates:
        with pytest.raises(ValueError) as err:
            Utils.date_difference(bad_date, bad_date)


def test_get_temp_dir_by_env(mocker):
    mocker.patch('os.path.exists', return_value=True)

    import os
    from lib.utils import Utils

    # unset all tmp variables
    for env_var in ['TMPDIR', 'TEMP', 'TMP']:
        os.environ[env_var] = ''

    for env_var in ['TMPDIR', 'TEMP', 'TMP']:
        value = '/test/{}/path/'.format(str.lower(env_var))
        os.environ[env_var] = value
        assert Utils.get_temp_dir() == value
        os.environ[env_var] = ''


def test_get_temp_dir_fallback(mocker):
    mock_os_path = mocker.patch('os.path.exists')

    # os.path.exists shall return one value per call from the following list.
    mock_os_path.side_effect = [True,               # /tmp: True
                                False, True,        # /tmp: False, /var/tmp: True
                                False, False, True  # /tmp: False, /var/tmp: False, c:\\windows\\temp: True
                                ]

    import os
    from lib.utils import Utils

    for env_var in ['TMPDIR', 'TEMP', 'TMP']:
        os.environ[env_var] = ''

    for path_val in ['/tmp', '/var/tmp', 'c:\\windows\\temp']:
        assert Utils.get_temp_dir() == path_val


def test_delete_files(mocker):
    mock_unlink = mocker.patch('os.unlink')
    from lib.utils import Utils

    for files_list in [['0'], ['0', '1'], ['0', '1', '2'], ['0', '1', '2', '3']]:
        Utils.delete_files(files_list)
        assert mock_unlink.call_count == len(files_list)
        mock_unlink.assert_has_calls([call(x) for x in files_list])
        mock_unlink.reset_mock()


def test_sanitize():
    from lib.utils import Utils

    data_items = {
        'abcdefghijklmnopqrstuvwxyz': 'abcdefghijklmnopqrstuvwxyz',     # alphabets
        'ABCDEFGHIJKLMNOPQRSTUVWXYZ': 'ABCDEFGHIJKLMNOPQRSTUVWXYZ',     # alphabets
        '0123456789': '0123456789',                                     # numbers
        'x.y.z': 'x.y.z',                                               # '.'
        'x:y:z': 'x:y:z',                                               # ':'
        'x/y/z': 'x/y/z',                                               # '/'
        'x\\y\\z': 'x\\y\\z',                                           # '\'
        'x-y-z': 'x-y-z',                                               # '-'
        'x_y_z': 'x_y_z',                                               # '_'
        'x--y---z': 'x-y-z',                                            # multiple '--'
        'x~!@#$%^&*()+={[}]|";,<>?` \'z': 'x-z',                        # everything else
        'xz~!@#$%^&*()+={[}]|";,<>?` \'': 'xz',                         # non-alphanum at end
        '/tmp/foo/ X Y Z /xyz.def` \'': '/tmp/foo/X-Y-Z/xyz.def',                         # non-alphanum around /
        '/tmp/foo/:-_. X _-_-_- Y  Z .../abc.def` \'': '/tmp/foo/X-Y-Z/abc.def',          # non-alphanum around /
        'c:\\windows\\tmp\\ _-123.pdf  ': 'c:\\windows\\tmp\\123.pdf',                    # non-alphanum around \
    }

    for key, val in data_items.items():
        assert Utils.sanitize(key) == val


def test_add_new_fields(mocker):
    mock_config_load = mocker.patch('lib.config.Config.load')
    mock_config_load.side_effect = [
        {'allowed_ext': ['ppt', 'pdf']},
        {'subjectName': {'long_subject_name': 'short_name'}}
    ]

    metadata_given = {
        'ttid': '123',
        'seqNo': 5,
        'views': 234,
        'actualDuration': 7260,
        'sessionId': 987,
        'startTime': '2021-01-31 09:00:05',
        'endTime': '2021-01-31 11:05:05',
        'subjectName': 'long_subject_name',
    }
    metadata_processed = {
        'ttid': '123',
        'seqNo': '05',                          # 2 digit fixed width string
        'views': '0234',                        # 4 digit fixed width string
        'actualDuration': '07260',              # 5 digit fixed width string
        'actualDurationReadable': '2:01h',      # from actualDuration field
        'sessionId': '0987',                    # 4 digit fixed width string.
        'startTime': '2021-01-31 09:00:05',
        'startDate': '2021-01-31',              # computed from startTime
        'endTime': '2021-01-31 11:05:05',
        'endDate': '2021-01-31',                # computed from endTime
        'subjectName': 'long_subject_name',
        'subjectNameShort': 'short_name',       # from subjectName mapping
        'ext': 'pdf'                           # since {'ttid': 123} has a associated attachment as: /foo/bar/baz.pdf
    }

    video_slide_mapping = {
        '123': '/foo/bar/baz.pdf',
        '456': '/foobaz/bar.pptx',
        '789': '/bazbar/foo.docx',
        # ...
    }
    from lib.utils import Utils

    assert Utils.add_new_fields(metadata_given) == metadata_processed
