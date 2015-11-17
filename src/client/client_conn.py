import encrypt
import filelist
import log
import json


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
    filelist.listing()
    download_file("testing.txt", "saveas.txt")
