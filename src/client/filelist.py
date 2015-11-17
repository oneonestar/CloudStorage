"""
List contains a list of user files with key, iv and tag.
"""

# External modules
import pyscrypt
import codecs
import json
import os

# Internal modules
import encrypt

__all__ = ["append", "save", "load"]

# filename_ori is the key.
mylist = {}

def append(filename_ori, filename_rand, key, iv, tag):
    """
    Append a new record into the list. filename_ori is the key.
    """
    list_record = {
        "filename_ori": filename_ori,
        "filename_rand": filename_rand,
        "key": key,
        "iv": iv,
        "tag": tag
    }
    mylist[list_record['filename_ori']] = list_record

def encrypt_list(password, salt):
    """
    Encrypt the list in JSON form. Return the encrypted byte.
    """
    mystr = {"array": []}
    for key, value in mylist.items():
        mystr["array"].append(value)
    data = json.dumps(mystr)
    return encrypt_data(password, salt, data.encode(encoding='UTF-8'))

def save(password, salt, filename="list"):
    """
    Save the encrypted list into a file using password and salt.

    Raise an exception when IO error.
    """
    data = encrypt_list(password, salt)
    try:
        with open(filename, "wb") as f:
            f.write(data)
    except Exception as e:
        log.print_exception(e)
        log.print_error("IO error", "cannot write to file '%s'" % (filename))
        raise

def load(password, salt, filename="list"):
    """
    Load the encrypted list from a file and store it into mylist[]

    Raise an exception when decryption failed.
    Tag unmatch will cause decryption fail.
    """
    mylist = {}
    data = None
    try:
        with open(filename, "rb") as f:
            data = f.read()
    except Exception as e:
        log.print_exception(e)
        log.print_error("IO error", "cannot read file '%s'" % (filename))
        raise

    # Decrypt
    iv = data[:12]
    tag = data[12: 12+16]
    cipher = data[12+16:]
    ret = decrypt_data(password, salt, iv, tag, cipher)
    ret = json.loads(ret.decode(encoding='UTF-8'))
    for i in ret["array"]:
        mylist[i['filename_rand']] = i

def encrypt_data(user_password, salt, data):
    """
    Encrypt the data and store it in form of [IV,TAG,CIPHER].
    """
    key = pyscrypt.hash(password = user_password.encode(encoding='UTF-8'), salt = salt.encode(encoding='UTF-8'), N = 1024, r = 1, p = 1, dkLen = 32)
    #print(codecs.encode(key, 'hex'))
    iv = os.urandom(12)
    ret = encrypt.encrypt(key, iv, data)
    #print(b''.join([iv, ret["tag"], ret["cipher"]]))
    return b''.join([iv, ret["tag"], ret["cipher"]])

def decrypt_data(user_password, salt, iv, tag, data):
    """
    Decrypt the data in form of [IV,TAG,CIPHER].

    Raise exception when failed to decrypt file.
    """
    key = pyscrypt.hash(password = user_password.encode(encoding='UTF-8'), salt = salt.encode(encoding='UTF-8'), N = 1024, r = 1, p = 1, dkLen = 32)
    #print(codecs.encode(key, 'hex'))
    ret = encrypt.decrypt(key, iv, tag, data)
    return ret

if __name__ == "__main__":
    '''
    For testing
    '''
    append("ori1", "rand1", "key1", "iv1", "tag1")
    append("ori2", "rand2", "key2", "iv2", "tag2")
    save("Password1", "salt1")
    load("Password1", "salt1")
    print(mylist)