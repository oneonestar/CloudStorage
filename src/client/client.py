import filelist
import client_conn


if __name__ == "__main__":
    '''
    For testing
    '''
    mylist = "list"
    password = "secure password"
    salt = "random salt"

    # Upload a file
    client_conn.upload_file("testing.txt")
    # List files
    filelist.listing()
    # Upload filelist
    filelist.save(password, salt, mylist)
    client_conn.upload(mylist)
    # Download filelist
    client_conn.download(mylist)
    # Download a file
    client_conn.download_file("testing.txt", "saveas.txt")
