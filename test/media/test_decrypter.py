import pytest
from mock import MagicMock


@pytest.fixture
def enc_keys():
    return [
        '0123456789abcdef',
        b'0123456789abcdef',
    ]


@pytest.fixture
def bad_enc_key_types():
    return [
        # not a str/byte type
        1234,
        0.1234,
    ]


@pytest.fixture
def bad_enc_key_lengths():
    return [
        # # not 16 chars/bytes
        '0123456789abcde',
        '0123456789abcdeff',
        b'0123456789abcde',
        b'0123456789abcdeff',
    ]


def test_decrypt_with_encryption_key(mocker, enc_keys):
    infile = '/tmp/1'
    mock_file = mocker.patch('builtins.open', mocker.mock_open(read_data='encrypted content'))

    mock_crypto = mocker.patch('Crypto.Cipher.AES.new')
    mock_crypto().decrypt = MagicMock(return_value='decrypted content')

    mocker.patch('os.path.join')

    from lib.media.decrypter import Decrypter

    for enc_key in enc_keys:
        Decrypter.decrypt(enc_key, infile, '/tmp')
        assert mock_file.call_count == 2
        mock_file.return_value.__enter__().write.assert_called_once_with('decrypted content')
        mock_file.reset_mock()


def test_decrypt_with_bad_encryption_key_types(mocker, bad_enc_key_types):
    infile = '/tmp/1'
    mocker.patch('os.path.join')

    from lib.media.decrypter import Decrypter

    for enc_key in bad_enc_key_types:
        with pytest.raises(AssertionError) as err:
            Decrypter.decrypt(enc_key, infile, '/tmp')
        assert 'Implement handling for type' in err.value.args[0]


def test_decrypt_with_bad_encryption_key_lengths(mocker, bad_enc_key_lengths):
    infile = '/tmp/1'
    mocker.patch('os.path.join')
    mock_file = mocker.patch('builtins.open', mocker.mock_open(read_data='encrypted content'))

    from lib.media.decrypter import Decrypter

    for enc_key in bad_enc_key_lengths:
        with pytest.raises(ValueError) as err:
            Decrypter.decrypt(enc_key, infile, '/tmp')
        assert 'Incorrect AES key length' in err.value.args[0]
