import encrypt
import filelist
import log
import json
import requests

def upload(filename_rand):
	url = "http://localhost:8080/api/add"
	#url = "https://www.onestar.moe"
	data = {'myinfo':'info1', 'myinfo2':'info2'}
	files = {'document': open(filename_rand, 'rb')}
	requests.packages.urllib3.disable_warnings()
	r = requests.post(url, data=data, files=files, verify=False)
	print(r.text)

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
    # TODO: upload cipher text to server

def download_file(filename_ori, saveas=None):
    """
    Download and decrypt the file. Output the file.

    Raise when filename_ori is not in filelist
    """
    # TODO: download file, save to filename_rand

    # Get the key, iv and tag from list
    record = None
    try:
        record = filelist.mylist[filename_ori]
    except:
        log.print_error("error", "file '%s' not in record" % (filename_ori))
        return

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
    upload("eb14a769-897f-471d-aada-0b58d38c04e5.data")
    filelist.listing()
    download_file("testing.txt", "saveas.txt")
