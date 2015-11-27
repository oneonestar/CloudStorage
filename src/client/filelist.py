"""
List contains a list of user files with key, iv and tag.
"""

# External modules
import pyscrypt
import binascii
import pickle
import os
import bson
import rsa
import encrypt
import base64
import copy

# Internal modules
import encrypt

__all__ = ["append", "save", "load", "listing"]

# filename_ori is the key.
mylist = {}
mylist_share = {}

def listing():
    """
    Display the records in filelist.
    """
    for i, k in mylist.items():
        print()
        print(i)
        import pprint
        pp = pprint.PrettyPrinter(indent=4)
        pp.pprint(k)
    for i, k in mylist_share.items():
        print()
        print(i)
        import pprint
        pp = pprint.PrettyPrinter(indent=4)
        pp.pprint(k)

def append(filename_ori, filename_rand, key, iv, tag):
    """
    Append a new record into the list. filename_ori is the key.
    """
    list_record = {
        "filename_ori": filename_ori,
        "filename_rand": filename_rand,
        "key": key,
        "iv": iv,
        "tag": tag,
    }
    mylist[filename_ori] = list_record

def append_share(filename_ori, filename_rand, key, iv, tag, shared_by):
    """
    Append a new record into the list. filename_ori is the key.
    """
    list_record = {
        "filename_ori": filename_ori,
        "filename_rand": filename_rand,
        "key": key,
        "iv": iv,
        "tag": tag,
        "shared_by": shared_by
    }
    mylist_share[filename_ori] = list_record

def export_record(filename_ori, sender, recipient, public_key, private_key):
    """
    Query a record, return a encrypted and signed BSON record

    public_key is the recipient's public key
    private_key is the sender's private key (i'm the sender)
    """
    if filename_ori not in mylist:
        return None
    # Prepare the record
    record = {}
    record = copy.deepcopy(mylist)[filename_ori]
    record["sender"] = sender
    record["recipient"] = recipient
    record_bson = bson.BSON.encode(record)

    # Sign and encrypt the record
    signature = rsa.sign_rsa(record_bson, private_key)
    final_record = {}
    final_record["signature"] = signature
    final_record["record"] = record_bson
    final_record_bson = bson.BSON.encode(final_record)

    # Use AES encrypt the record, use rsa to encrypt the symmetric key
    ret = encrypt.encrypt_rand(final_record_bson)
    ret_bin =  b''.join([ret["key"], ret["iv"], ret["tag"]])
    encrypted_final_record = rsa.encrypt_rsa(ret_bin, public_key)

    final = {
        "key": encrypted_final_record,
        "record": ret["cipher"]
    }
    return base64.b64encode(bson.BSON.encode(final))

def import_record(record, public_key, private_key):
    """
    Import an encrypted and signed BSON record

    public_key is the sender's public key
    private_key is the recipient's private key (i'm the recipient)
    """
    try:
        final = bson.BSON.decode(base64.b64decode(record))
        ret_bin = final['key']
        ret_bin = rsa.decrypt_rsa(ret_bin, private_key)
        key = ret_bin[:32]
        iv = ret_bin[32:32+12]
        tag = ret_bin[32+12: 32+12+16]
        final_record_bson = encrypt.decrypt(key, iv, tag, final['record'])
        final_record = bson.BSON.decode(final_record_bson)
        if not rsa.verify_rsa(final_record["record"],
                      final_record["signature"], public_key):
            print("Signature not match")
            raise Exception('signature not match')
        record = bson.BSON.decode(final_record["record"])
        return record
    except:
        print("Import record failed")
        raise

def delete(filename_ori):
    global mylist
    if filename_ori in mylist:
        mylist.pop(filename_ori, None)
    else:
        print("File not in the list")

def get(filename_ori):
    return mylist.get(filename_ori)

def encrypt_list(password, salt):
    """
    Encrypt the list in JSON form. Return the encrypted byte.
    """
    data = pickle.dumps(mylist, pickle.HIGHEST_PROTOCOL)
    return encrypt_data(password, salt, data)

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
    global mylist
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
    try:
        ret = decrypt_data(password, salt, iv, tag, cipher)
    except:
        return False
    mylist = pickle.loads(ret)

def encrypt_data(user_password, salt, data):
    """
    Encrypt the data and store it in form of [IV,TAG,CIPHER].
    """
    key = pyscrypt.hash(password = user_password.encode(encoding='UTF-8'), salt = salt.encode(encoding='UTF-8'), N = 1024, r = 1, p = 1, dkLen = 32)
    iv = os.urandom(12)
    ret = encrypt.encrypt(key, iv, data)
    return b''.join([iv, ret["tag"], ret["cipher"]])

def decrypt_data(user_password, salt, iv, tag, data):
    """
    Decrypt the data in form of [IV,TAG,CIPHER].

    Raise exception when failed to decrypt file.
    """
    key = pyscrypt.hash(password = user_password.encode(encoding='UTF-8'), salt = salt.encode(encoding='UTF-8'), N = 1024, r = 1, p = 1, dkLen = 32)
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

    # Test sharing record
    public_key = rsa.get_cert("oneonestar@gmail.com")
    if os.path.isfile("/home/star/.ssh/me.key.pem2"):
        private_key = rsa.load_private_cert_from_file("/home/star/.ssh/me.key.pem2")
    else:
        private_key = rsa.load_private_cert_from_file("key/private_key.pem")
    append("file1", "file-UUID", b'key', b'iv', b'tag')
    print(mylist)
    record = export_record("file1", "alice", "bob", public_key, private_key)
    print("record:", record)
    import_record(record, public_key, private_key)
