import filelist
import client_conn


if __name__ == "__main__":
    '''
    For testing
    '''
    mylist = "list"
    password = "secure password"
    salt = "random salt"

    #url = "https://blog.onestar.moe:8080"
    client_conn.setup("http://localhost:8080/", "../server/config/server.pem")
    client_conn.registration("STAR", "PW")
    #client_conn.setup("https://localhost:8080/", "../server/config/server.pem")
    #while True:
        #username = input()
        #password = input()
    status = client_conn.authenticate("star", "PW")
    status = client_conn.authenticate("STAR", "Pw")
    status = client_conn.authenticate("STAR", "PW")
     #   if status:
            # login success
     #       break

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
