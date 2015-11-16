# Encrypt file module
import os
import uuid
from cryptography import exceptions
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend

def encrypt_file(filename):
    '''
    Encrypt a file, store it into another file using random filename.
    Using random genereated key and iv for encryption.
    Return {original filename, random generate filename, key, iv, tag, cipher}
    '''
    # Read file
    with open(filename, "rb") as f:
        try:
            data = f.read()
        except:
            pass

    # Encrypt using random key and iv
    ret = encrypt_rand(data)

    # Write file using random filename
    filename_rand = str(uuid.uuid4())+".data"
    with open(filename_rand, "wb") as f:
        f.write(ret['cipher'])
    
    # Store original filename and generated random filename
    ret['filename'] = filename
    ret['filename_rand'] = filename_rand
    return ret

def decrypt_file(filename_ori, filename_rand, key, iv, tag):
    '''
    Decrypt a file.
    Return the decrypted byte array.
    '''
    ret = None
    # Read file
    with open(filename_rand, "rb") as f:
        try:
            data = f.read()
        except:
            pass

    # Decrypt
    ret = decrypt(key, iv, tag, data)
    print(ret)


def encrypt_rand(plainText):
    """
    Encrypt byte data. Generate a random key, iv and filename for encryption.
    Return {key, iv, tag, cipher}
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
    Return decrypted byte data.
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
        print("ComfortZone: decryption error: message have been modified")
        #raise
    return ret


if __name__ == "__main__":
    # Encrypt / Decrypt byte string
    ret = encrypt_rand(b"Testing Encryption")
    ret2 = decrypt(ret['key'], ret['iv'], ret['tag'], ret['cipher'])
    print(ret['cipher'])
    print(ret2)
    print(ret2.decode(encoding='UTF-8'))

    # Try modify + decrypt
    ret3 = decrypt(ret['key'], ret['iv'], ret['tag'], b"Fake message")
    print(ret3)

    # Encrypt / Decrypt file
    ret = encrypt_file("testing.txt")
    print(ret)
    decrypt_file(ret['filename'], ret['filename_rand'], ret['key'], ret['iv'], ret['tag'])
