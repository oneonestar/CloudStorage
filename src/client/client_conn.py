import encrypt
import filelist
import log
import json
import requests

base_url = None
cert = None
token = None

def setup(server_url, selfcert=None):
    global base_url
    global cert
    base_url = server_url
    cert = selfcert

def registration(username, password):
    url = base_url + "registration"
    payload = {
            'client_id': username,
            'client_secret': password
    }
    r = requests.post(url, data=payload, verify=cert)

    # Parse result
    try:
        response = json.loads(r.text)
    except Exception as e:
        log.print_exception(e)
        log.print_error("authentication failure", "failed to decode server message '%s'" % (r.text))
        return False
    if response.get("status"):
        print("Create ac success")
    else:
        print("Create ac failed")


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
    r = requests.post(url, data=payload, verify=cert)

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
        token = response.get("token")
        print(token)
        return True
    else:
        # Authentication failure
        log.print_error("authentication failure", "wrong username or password")
        return False

def upload(filename_rand):
    """
    Upload the file to server.
    """
    url = base_url+"upload"
    data = {'token': token}
    files = {'document': open(filename_rand, 'rb')}
    #r = requests.post(url, data=data, files=files, verify=True)
    r = requests.post(url, data=data, files=files, verify=cert)
    files['document'].close()
    # Parse result
    try:
        response = json.loads(r.text)
    except Exception as e:
        log.print_exception(e)
        log.print_error("authentication failure", "failed to decode server message '%s'" % (r.text))
        return False
    if response.get("status"):
        print("Upload success")
    else:
        print("Upload failed")

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
        return

    # Store the filename, key, iv and tag to list
    filelist.append(data["filename_ori"], data["filename_rand"], data["key"],
                    data["iv"], data["tag"])
    # Upload cipher text to server
    upload(data["filename_rand"])

def download(filename_rand):
    url = base_url+filename_rand
    data = {'token': token}
    #r = requests.get(url, data=data, verify=True)
    r = requests.get(url, params=data, verify=cert)
    try:
        with open(filename_rand, "wb") as f:
            f.write(r.content)
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
    try:
        record = filelist.mylist[filename_ori]
    except:
        log.print_error("error", "file '%s' not in record" % (filename_ori))
        return

    r = download(record["filename_rand"])

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
        return

if __name__ == "__main__":
    '''
    For testing
    '''
    upload_file("testing.t")
    upload_file("testing.txt")
    filelist.listing()
    _ = input()
    download_file("testing.txt", "saveas.txt")
