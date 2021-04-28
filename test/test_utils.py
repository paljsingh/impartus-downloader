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
