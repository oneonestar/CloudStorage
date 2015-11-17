import encrypt
import filelist
import log
import json
import requests

url = "https://localhost:8080/"
cert = "../server/config/server.pem"
#url = "https://blog.onestar.moe:8080"

def upload(filename_rand):
    """
    Upload the file to server.
    """
    url2 = url+filename_rand
    data = {'user':filename_rand}
    files = {'document': open(filename_rand, 'rb')}
    #r = requests.post(url, data=data, files=files, verify=True)
    r = requests.post(url2, data=data, files=files, verify=cert)
    files['document'].close()

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
    url2 = url+filename_rand
    payload = {'user':filename_rand}
    #r = requests.get(url2, data=data, verify=True)
    r = requests.get(url2, verify=cert)
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
