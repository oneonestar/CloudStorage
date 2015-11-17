import encrypt
import filelist
import log
import json
import requests

url = "https://localhost:8080"

def upload(filename_rand):
    """
    Upload the file to server.
    """
    data = {'command':'upload', 'filename':filename_rand}
    files = {'document': open(filename_rand, 'rb')}
    #requests.packages.urllib3.disable_warnings()
    #r = requests.post(url, data=data, files=files, verify=True)
    r = requests.post(url, data=data, files=files, verify="/home/star/Documents/yr3/CloudStorage/src/server/server.pem")
    #r = requests.post(url, data=data, files=files, verify=False)

def upload_file(filename_ori):
    """
    Encrypt and upload the file, also add record in list.
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
    data = {'command':'download', 'filename':filename_rand}
    requests.packages.urllib3.disable_warnings()
    r = requests.post(url, data=data, verify=False)

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

    download(record["filename_rand"])

    if saveas == None:
        outputfile = filename_ori
    else:
        outputfile = saveas
    encrypt.decrypt_file(outputfile, record["filename_rand"],
                         record["key"], record["iv"], record["tag"])

if __name__ == "__main__":
    '''
    For testing
    '''
    upload_file("testing.t")
    upload_file("testing.txt")
    upload_file("testing.txt")
    filelist.listing()
    download_file("testing.txt", "saveas.txt")
