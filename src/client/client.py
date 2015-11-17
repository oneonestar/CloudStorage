import filelist
import client_conn


if __name__ == "__main__":
    '''
    For testing
    '''
    client_conn.upload_file("testing.t")
    client_conn.upload_file("testing.txt")
    client_conn.upload_file("testing.txt")
    filelist.listing()
    client_conn.download_file("testing.txt", "saveas.txt")
