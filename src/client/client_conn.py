import encrypt
import filelist
import log
import json
import requests
import os
import rsa

base_url = None
cert = None
token = None
client_id = None

##################################################################
# Initial setup, such as setting the server and certificates
##################################################################
def setup(server_url, selfcert=None):
    global base_url
    global cert
    base_url = server_url
    cert = selfcert

##################################################################
# Registrate a new account
##################################################################
def registrate(username, password):
    url = base_url + "registration"
    payload = {
            'client_id': username,
            'client_secret': password
    }
    try:
        r = requests.post(url, data=payload, verify=cert)
    except Exception as e:
        log.print_exception(e)
        log.print_error("error", "connection failure")
        return False

    # Parse result
    try:
        response = json.loads(r.text)
    except Exception as e:
        log.print_exception(e)
        log.print_error("authentication failure", "failed to decode server message '%s'" % (r.text))
        return False
    if response.get("status"):
        return True
    else:
        return False


##################################################################
# Login
##################################################################
def authenticate(username, password):
    url = base_url + "login"
    payload = {
            'client_id': username,
            'client_secret': password
    }
    # Request to server
    # For real cert
    # r = requests.get(url, data=data, verify=True)
    # For self cert
    try:
        r = requests.post(url, data=payload, verify=cert)
    except Exception as e:
        log.print_exception(e)
        log.print_error("error", "connection failure")
        return False

    # Parse result
    try:
        response = json.loads(r.text)
    except Exception as e:
        log.print_exception(e)
        log.print_error("authentication failure", "failed to decode server message '%s'" % (r.text))
        return False
    if response.get("status", False) and response.get("token", None) != None:
        # Authentication success
        global token
        global client_id
        token = response.get("token")
        client_id = username
        return True
    else:
        # Authentication failure
        log.print_error("authentication failure", "wrong username or password")
        return False

##################################################################
# Logout
##################################################################
def logout():
    global token
    if token == None:
        return False
    url = base_url + "logout"
    data = {"token": token}
    #r = requests.get(url, data=data, verify=True)
    try:
        r = requests.get(url, params=data, verify=cert)
    except Exception as e:
        log.print_exception(e)
        log.print_error("error", "connection failure")
        return False
    # Parse result
    try:
        response = json.loads(r.text)
    except Exception as e:
        log.print_exception(e)
        log.print_error("logout failed", "failed to decode server message '%s'" % (r.text))
        return False

    if response.get("status", False):
        token = None
        # Logout successful
        return True
    else:
        # Logout failure
        log.print_error("logout failed", "failed to logout '%s'" % (r.text))
        print("d")
        return False

##################################################################
# Is login
##################################################################
def is_login():
    return token != None
def username():
    return client_id

##################################################################
# Upload file
##################################################################
def upload(filename_rand):
    """
    Upload the file to server.
    """
    url = base_url+"upload"
    data = {'token': token}
    files = {'document': open(filename_rand, 'rb')}
    #r = requests.post(url, data=data, files=files, verify=True)
    try:
        r = requests.post(url, data=data, files=files, verify=cert)
    except Exception as e:
        log.print_exception(e)
        log.print_error("error", "connection failure")
        return False
    files['document'].close()
    # Parse result
    try:
        response = json.loads(r.text)
    except Exception as e:
        log.print_exception(e)
        log.print_error("authentication failure", "failed to decode server message '%s'" % (r.text))
        return False
    if response.get("status"):
        return True
    else:
        return False

def upload_file(filename_ori):
    """
    Encrypt and upload the file using random filename, also add record in list.
    """
    # Encrypt the file
    data = None
    try:
        data = encrypt.encrypt_file(filename_ori)
    except:
        log.print_error("error", "failed to encrypt file '%s'" % (filename_ori))
        return False

    # Store the filename, key, iv and tag to list
    filelist.append(data["filename_ori"], data["filename_rand"], data["key"],
                    data["iv"], data["tag"])
    # Upload cipher text to server
    return upload(data["filename_rand"])

##################################################################
# Delete file
##################################################################
def delete(filename_rand):
    """
    Upload the file to server.
    """
    url = base_url
    data = {
        'token': token,
        'file': filename_rand
    }
    try:
        r = requests.delete(url, params=data, verify=cert)
    except Exception as e:
        log.print_exception(e)
        log.print_error("error", "connection failure")
        return False
    # Parse result
    try:
        response = json.loads(r.text)
    except Exception as e:
        log.print_exception(e)
        log.print_error("authentication failure", "failed to decode server message '%s'" % (r.text))
        return False
    if response.get("status"):
        return True
    else:
        return False


##################################################################
# Download file
##################################################################
def download(filename_rand, saveas=None, shared_by=None):
    '''
    Download and save the file from server.
    '''
    if saveas == None:
        saveas = filename_rand
    url = base_url+"download"
    data = {
        'token': token,
        'file': filename_rand
    }
    if shared_by != None:
        data['shared_by'] = shared_by
    #r = requests.get(url, data=data, verify=True)
    try:
        r = requests.get(url, params=data, verify=cert)
    except Exception as e:
        log.print_exception(e)
        log.print_error("error", "connection failure")
        return False
    if r.content == b'404 page not found\n':
        return False
    try:
        with open(saveas, "wb") as f:
            f.write(r.content)
        return True
    except Exception as e:
        log.print_exception(e)
        log.print_error("IO error", "cannot open file '%s'" % (filename_rand))
        raise

def download_file(filename_ori, saveas=None):
    """
    Download and decrypt the file. Output the file.

    Raise when filename_ori is not in filelist
    """

    # Get the key, iv and tag from list
    record = None
    if filename_ori in filelist.mylist:
        record = filelist.mylist[filename_ori]
        r = download(record["filename_rand"])
    elif filename_ori in filelist.mylist_share:
        record = filelist.mylist_share[filename_ori]
        r = download(record["filename_rand"], record["shared_by"])
    else:
        log.print_error("error", "file '%s' not in record" % (filename_ori))
        return False

    if saveas == None:
        outputfile = filename_ori
    else:
        outputfile = saveas

    # Try decryption
    try:
        encrypt.decrypt_file(outputfile, record["filename_rand"],
                             record["key"], record["iv"], record["tag"])
    except:
        log.print_error("error", "failed to decrypt '%s'" % (filename_ori))
        return False
    return True

##################################################################
# Share file
##################################################################
def share(recipient, data):
    """
    Upload the file to server.
    """
    url = base_url+"share"
    print(token)
    print(recipient)
    print(data)
    data = {
        'token': token,
        'recipient': recipient,
        'data': data
    }
    try:
        r = requests.post(url, data=data, verify=cert)
    except Exception as e:
        log.print_exception(e)
        log.print_error("error", "connection failure")
        return False
    # Parse result
    try:
        response = json.loads(r.text)
        print(response)
    except Exception as e:
        log.print_exception(e)
        log.print_error("authentication failure", "failed to decode server message '%s'" % (r.text))
        return False
    if response.get("status"):
        return True
    else:
        return False

##################################################################
# Get share file
##################################################################
def get_share():
    """
    Upload the file to server.
    """
    url = base_url+"listshare"
    data = {
        'token': token,
    }
    data = {"token": token}
    try:
        r = requests.get(url, params=data, verify=cert)
    except Exception as e:
        log.print_exception(e)
        log.print_error("error", "connection failure")
        return False
    # Parse result
    try:
        response = json.loads(r.text)
        print(response)
    except Exception as e:
        log.print_exception(e)
        log.print_error("authentication failure", "failed to decode server message '%s'" % (r.text))
        return False
    if not response.get("status"):
        return False
    if response["records"] == None:
        return False
    for i in response["records"]:
        sender = i['Sender']
        record = i['Record']
        print("Sender:",sender)
        print("Record:",record)
        try:
            if os.path.isfile("/home/star/.ssh/me.key.pem2"):
                public_key = rsa.get_cert("oneonestar@gmail.com")
            else:
                public_key = rsa.load_public_cert_from_file("key/public_key.pem")
            if os.path.isfile("/home/star/.ssh/me.key.pem2"):
                private_key = rsa.load_private_cert_from_file("/home/star/.ssh/me.key.pem2")
            else:
                private_key = rsa.load_private_cert_from_file("key/private_key.pem")
            share = filelist.import_record(record, public_key, private_key)
            print(share)
            if share != None:
                filelist.append_share(share['filename_ori'], share['filename_rand'],
                            share['key'], share['iv'], share['tag'], sender)
        except:
            print("Failed to decrypt message")
            pass

if __name__ == "__main__":
    '''
    For testing
    '''
    upload_file("testing.t")
    upload_file("testing.txt")
    filelist.listing()
    _ = input()
    download_file("testing.txt", "saveas.txt")
