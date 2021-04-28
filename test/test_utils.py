import pytest
from mock import MagicMock


@pytest.fixture
def enc_keys():
    return [
        '0123456789abcdef',
        b'0123456789abcdef',
    ]


def test_move_and_rename_file(mocker):
    mocker.patch('os.makedirs')
    mocker.patch('os.path.dirname')
    mock_move = mocker.patch('shutil.move')

    from app.utils import Utils

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
    from app.utils import Utils

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
    from app.utils import Utils

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
    mock_os_path.side_effect = [True,           # /tmp, return true immediately
                                False, True,    # /tmp: False, /var/tmp: True
                                False, False, True  # /tmp: False, /var/tmp: False, c:\\windows\\temp: True
                                ]

    import os
    from app.utils import Utils

    for env_var in ['TMPDIR', 'TEMP', 'TMP']:
        os.environ[env_var] = ''

    for path_val in ['/tmp', '/var/tmp', 'c:\\windows\\temp']:
        assert Utils.get_temp_dir() == path_val
