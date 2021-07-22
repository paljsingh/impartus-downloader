from Crypto.Cipher import AES   # noqa
from typing import Any
import os


class Decrypter:
    """
    Utility functions for decrypting AES-128 encrypted streams.
    """
    def __init__(self):
        pass

    @classmethod
    def decrypt(cls, encryption_key: Any, in_filepath: str, out_dir: str) -> str:
        """
        Given an encryption key and input filepath, decrypt the file using AES-128 bit decryption.
        Return filepath to the decrypted file.
        :param cls: class name.
        :param encryption_key: Encryption key (string and bytes type supported)
        :param in_filepath: Input file path.
        :param out_dir: Directory path where decrypted contents are to be saved.
        :Return : decrypted file path if key exists, input filepath otherwise.
        """
        out_filepath = os.path.join(out_dir, os.path.basename(in_filepath) + ".ts")  # default path

        if encryption_key:
            if type(encryption_key) == str:
                dec_key_bytes = bytes(encryption_key, 'utf-8')
            elif type(encryption_key) == bytes:
                dec_key_bytes = encryption_key
            else:
                assert False, "Implement handling for type {}".format(type(encryption_key))

            iv = bytes('\0' * 16, 'utf-8')
            with open(out_filepath, 'wb+') as out_fh:
                with open(in_filepath, 'rb') as in_fh:
                    ciphertext = in_fh.read()
                    aes = AES.new(dec_key_bytes, AES.MODE_CBC, iv)
                    out_fh.write(aes.decrypt(ciphertext))
        else:
            # nothing to be done.
            out_filepath = in_filepath

        return out_filepath
