import pytest
from mock import call
from mock import PropertyMock
import logging


@pytest.fixture
def tests_data():
    return [
        {
            'desc': 'Single Track - use input ts file as is',
            'duration': 10,
            'files': ['0.ts'],
            'filepath': '/tmp/test1.mkv',
            'split_calls': [call('ffmpeg -y -loglevel quiet -i 0.ts -c copy -ss 0 -t 10 tmp.ts')],
            'encode_calls': [call('ffmpeg -y -loglevel quiet -analyzeduration 2147483647 -probesize 2147483647'
                                  + ' -i 0.ts -metadata ttid=1234 -c copy -map 0 /tmp/test1.mkv')],
            'exception': '[1234]: Check the ts file(s) generated at location: 0.ts',
        },
        {
            'desc': 'Multi Track - Split 0.ts content into 0.ts and 1.ts',
            'duration': 10,
            'files': ['0.ts', '1.ts'],
            'filepath': '/tmp/test2.mkv',
            'split_calls': [
                call('ffmpeg -y -loglevel quiet -i 0.ts -c copy -ss 10 -t 10 1.ts'),
                call('ffmpeg -y -loglevel quiet -i 0.ts -c copy -ss 0 -t 10 tmp.ts')],
            'encode_calls': [call('ffmpeg -y -loglevel quiet -analyzeduration 2147483647 -probesize 2147483647'
                                  + ' -i 0.ts -analyzeduration 2147483647 -probesize 2147483647 -i 1.ts'
                                  + ' -metadata ttid=1234 -c copy -map 0 -map 1 /tmp/test2.mkv')],
            'exception': '[1234]: Check the ts file(s) generated at location: 0.ts, 1.ts',
        },
        {
            'desc': 'Multi Track - Split 0.ts content into 0.ts, 1.ts and 2.ts',
            'duration': 10,
            'files': ['0.ts', '1.ts', '2.ts'],
            'filepath': '/tmp/test3.mkv',
            'split_calls': [
                call('ffmpeg -y -loglevel quiet -i 0.ts -c copy -ss 10 -t 10 1.ts'),
                call('ffmpeg -y -loglevel quiet -i 0.ts -c copy -ss 20 -t 10 2.ts'),
                call('ffmpeg -y -loglevel quiet -i 0.ts -c copy -ss 0 -t 10 tmp.ts')],
            'encode_calls': [call('ffmpeg -y -loglevel quiet -analyzeduration 2147483647 -probesize 2147483647'
                                  + ' -i 0.ts -analyzeduration 2147483647 -probesize 2147483647 -i 1.ts'
                                  + ' -analyzeduration 2147483647 -probesize 2147483647 -i 2.ts -metadata ttid=1234'
                                  + ' -c copy -map 0 -map 1 -map 2 /tmp/test3.mkv')],
            'exception': '[1234]: Check the ts file(s) generated at location: 0.ts, 1.ts, 2.ts',
        }
    ]


def test_split_track(mocker, tests_data):
    mocker.patch('shutil.move')
    os_system = mocker.patch('os.system')
    from lib.media.encoder import Encoder

    for test_data in tests_data:
        Encoder.split_track(test_data['files'], test_data['duration'], priority='low')
        assert os_system.call_count == len(test_data['files'])
        os_system.assert_has_calls(test_data['split_calls'])
        os_system.reset_mock()


def test_encode_mkv_no_split(mocker, tests_data):
    os_system = mocker.patch('os.system')
    mocker.patch('os.stat')
    from lib.media.encoder import Encoder

    for test_data in tests_data:
        Encoder.encode_mkv(1234, test_data['files'], test_data['filepath'], test_data['duration'], debug=False)
        assert os_system.call_count == 1
        os_system.assert_has_calls(test_data['encode_calls'])
        os_system.reset_mock()


def test_encode_mkv_with_split(mocker, tests_data):
    os_system = mocker.patch('os.system')

    # mock os.stat.st_size to return 0, so that the split branch is called.
    os_stat = mocker.patch('os.stat')
    type(os_stat.return_value).st_size = PropertyMock(return_value=0)

    from lib.media.encoder import Encoder

    for test_data in tests_data:
        Encoder.encode_mkv(1234, test_data['files'], test_data['filepath'], test_data['duration'], debug=False)
        assert os_system.call_count == 1 + len(test_data['files'])
        os_system.assert_has_calls(*[test_data['split_calls'], test_data['encode_calls']])
        os_system.reset_mock()


def test_encode_mkv_with_exception(mocker, tests_data, caplog):
    # mock os.system to throw an exception.
    os_system = mocker.patch('os.system')
    os_system.side_effect = Exception('os.system error!')

    mocker.patch('os.stat')

    from lib.media.encoder import Encoder

    for test_data in tests_data:
        output = Encoder.encode_mkv(1234, test_data['files'], test_data['filepath'], test_data['duration'], debug=False)
        assert os_system.call_count == 1
        assert output is False

        capiter = iter(caplog.records)
        assert len(caplog.records) == 2
        record = next(capiter)
        assert record.message == '[1234]: ffmpeg exception: os.system error!'
        assert record.levelno == logging.ERROR
        assert record.module == 'encoder'
        record2 = next(capiter)
        assert record2.message == test_data['exception']
        assert record2.levelno == logging.ERROR
        assert record2.module == 'encoder'
        os_system.reset_mock()
        caplog.clear()


def test_join(mocker, tests_data):
    mocker.patch('os.path.join')
    mock_open = mocker.patch("builtins.open")

    from lib.media.encoder import Encoder

    stream_files = ["1", "2", "3", "4"]
    Encoder.join(stream_files, "/tmp", 0)
    assert mock_open.call_count == 1 + len(stream_files)

