from Crypto.Cipher import AES  # noqa
import os

class Decrypter:

    def __init__(self):
        pass

    @classmethod
    def decrypt(cls, encryption_key, in_filepath, out_dir):
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
