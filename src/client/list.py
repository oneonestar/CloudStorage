# External modules
import pyscrypt
import codecs
import json
import os

# Internal modules
import encrypt
mystr = {
    "array": [
        {"filename":"a", "cipher":"b"},
        {"filename":"c", "cipher":"d"},
    ]
}

mylist = {}
def append(filename_ori, filename_rand, key, iv, tag):
    list_record = {
        "filename_ori": filename_ori,
        "filename_rand": filename_rand,
        "key": key,
        "iv": iv,
        "tag": tag
    }
    mylist[list_record['filename_rand']] = list_record

def encrypt_list(password, salt):
    mystr = {"array": []}
    for key, value in mylist.items():
        mystr["array"].append(value)
    data = json.dumps(mystr)
    return encrypt_data(password, salt, data.encode(encoding='UTF-8'))

def save(password, salt, filename="list"):
    data = encrypt_list(password, salt)
    with open(filename, "wb") as f:
        f.write(data)

def load(password, salt, filename="list"):
    mylist = {}
    data = None
    with open(filename, "rb") as f:
        data = f.read()

    # Decrypt
    iv = data[:12]
    tag = data[12: 12+16]
    cipher = data[12+16:]
    ret = decrypt_data(password, salt, iv, tag, cipher)
    ret = json.loads(ret.decode(encoding='UTF-8'))
    for i in ret["array"]:
        mylist[i['filename_rand']] = i

def encrypt_data(user_password, salt, data):
    key = pyscrypt.hash(password = user_password.encode(encoding='UTF-8'), salt = b"seasalt", N = 1024, r = 1, p = 1, dkLen = 32)
    #print(codecs.encode(key, 'hex'))
    iv = os.urandom(12)
    ret = encrypt.encrypt(key, iv, data)
    #print(b''.join([iv, ret["tag"], ret["cipher"]]))
    return b''.join([iv, ret["tag"], ret["cipher"]])

def decrypt_data(user_password, salt, iv, tag, data):
    key = pyscrypt.hash(password = user_password.encode(encoding='UTF-8'), salt = b"seasalt", N = 1024, r = 1, p = 1, dkLen = 32)
    #print(codecs.encode(key, 'hex'))
    ret = encrypt.decrypt(key, iv, tag, data)
    return ret

if __name__ == "__main__":
    #encrypt_list("PW1", "S1",b"DATA")

    append("ori1", "rand1", "key1", "iv1", "tag1")
    append("ori2", "rand2", "key2", "iv2", "tag2")
    save("Password1", "salt1")
    load("Password1", "salt1")
    print(mylist)
    #save()
    #load()
