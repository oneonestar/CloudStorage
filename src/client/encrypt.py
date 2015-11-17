"""
Encryption module using AES-256-GCM
"""

import os
import uuid
from cryptography import exceptions
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend

# For logging
import log

#__all__ = 

def encrypt_file(filename_ori):
    '''
    Encrypt a file and store the ciphertext into another file.

    This function will generate a random key and iv for encryption.
    The filename of the output file will be randomly generated.
    
    Return a dict containing:
    {original filename, randomly generated filename, key, iv, tag}

    Raise IOError when failed to open the file.
    '''

    # Read file
    data = None
    try:
        with open(filename_ori, "rb") as f:
            data = f.read()
    except Exception as e:
        log.print_exception(e)
        log.print_error("IO error", "cannot open file '%s'" % (filename_ori))
        raise

    # Encrypt using random key and iv
    ret = encrypt_rand(data)

    # Write ciphertext using random filename
    filename_rand = str(uuid.uuid4())+".data"
    try:
        with open(filename_rand, "wb") as f:
            f.write(ret['cipher'])
    except Exception as e:
        log.print_exception(e)
        log.print_error("IO error", "cannot write to file '%s'"
						% (filename_rand))
        raise
    
    # Store original filename and the generated filename
    ret.pop("cipher", None)
    ret['filename_ori'] = filename_ori
    ret['filename_rand'] = filename_rand
    return ret

def decrypt_file(filename_ori, filename_rand, key, iv, tag):
    '''
    Decrypt a file and write the plaintext to filename_ori.

    Raise error when failed to open/write file or decryption error.
    Any modification to the cipher will cause the decryption to fail.
    '''
    ret = None
    # Read file
    try:
        with open(filename_rand, "rb") as f:
            data = f.read()
    except Exception as e:
        log.print_exception(e)
        log.print_error("IO error", "cannot open file '%s'" % (filename_rand))
        raise

    # Decrypt
    try:
        ret = decrypt(key, iv, tag, data)
    except:
        log.print_exception(e)
        log.print_error("error", "failed to decrypt message")
        raise

    # Write to filename_ori
    try:
        with open(filename_ori, "wb") as f:
            data = f.write(ret)
    except Exception as e:
        log.print_exception(e)
        log.print_error("IO error", "cannot write to file '%s'"
						% (filename_rand))
        raise

def encrypt_rand(plainText):
    """
    Encrypt byte data. Generate a random key and iv for encryption.

    Return a dict contains {key, iv, tag, cipher}
    """

    # Generate a random 96-bit IV
    iv = os.urandom(12)
    # Generate a random 256-bit Key
    key = os.urandom(32)

    data = encrypt(key, iv, plainText)
    ret = {
        "key": key,
        "iv": iv,
        "tag": data['tag'],
        "cipher": data['cipher']
    }
    return ret

def encrypt(key, iv, plainText):
    '''
    Encrypt data using key and iv.

    Return cipher text and tag.
    '''
    # Construct an AES-GCM Cipher object with the given key and IV
    encryptor = Cipher(
        algorithms.AES(key),
        modes.GCM(iv),
        backend=default_backend()
    ).encryptor()

    cipherText = encryptor.update(plainText) + encryptor.finalize()
    return ({"cipher": cipherText, "tag":encryptor.tag})


def decrypt(key, iv, tag, cipherText):
    '''
    Decrypt byte data using the given key, iv and tag.

    Return the decrypted byte data.

    Raise exception when MAC tag didn't match.
    '''
    decryptor = Cipher(
        algorithms.AES(key),
        modes.GCM(iv, tag),
        backend=default_backend()
    ).decryptor()

    # Decryption gets us the authenticated plaintext.
    # If the tag does not match an InvalidTag exception will be raised.
    ret = None
    try:
        ret = decryptor.update(cipherText) + decryptor.finalize()
    except exceptions.InvalidTag:
        log.print_error("decrytion error", "message have been modified")
        raise
    return ret


if __name__ == "__main__":
    '''
    For testing
    '''
    # Encrypt / Decrypt byte string
    print("=============================")
    print("Encrypt / Decrypt byte string")
    ret = encrypt_rand(b"Testing Encryption")
    ret2 = decrypt(ret['key'], ret['iv'], ret['tag'], ret['cipher'])
    print(ret['cipher'])
    print(ret2)
    print(ret2.decode(encoding='UTF-8'))

    print("=============================")
    print("Try modify data + decrypt")
    # Try modify + decrypt
    try:
        ret = decrypt(ret['key'], ret['iv'], ret['tag'], b"Fake message")
        print(ret)
    except:
        log.print_error("error", "failed to decrypt file")

    print("=============================")
    print("Encrypt non-existing file")
    # Encrypt non-existing file
    try:
        ret = encrypt_file("testing.t")
        print(ret)
    except:
        log.print_error("error", "failed to encrypt file")

    print("=============================")
    print("Encrypt / Decrypt file")
    try:
        ret = encrypt_file("testing.txt")
        print(ret)
    except:
        log.print_error("error", "failed to encrypt file")
    try:
        decrypt_file(ret['filename_ori']+".out", ret['filename_rand'],
					 ret['key'], ret['iv'], ret['tag'])
    except:
        log.print_error("error", "failed to decrypt file")
