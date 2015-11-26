import client_conn
import filelist
import rsa
import hashlib
import getpass
import log
import os
import signal
import sys

# filename of list
mylist = "list"
password = None


def print_help():
    """
    Print the available command list.
    """
    print()
    print()
    if client_conn.is_login():
        print("Login as: "+ client_conn.username())
    print("Help:")
    print("General:")
    print("  c   create a new account")
    print("  i   login")
    print("  o   logout")
    print("  p   print this menu")
    print("  q   logout and quit")
    print()
    print("Files:")
    print("  d   download file")
    print("  l   list file")
    print("  r   delete file")
    print("  s   share file")
    print("  u   upload file")
    print()

def event_loop():
    """
    Main input event loop.
    """
    # Get input
    print()
    print("Command (p for help): ", end="")
    command = input().strip()
    # General
    if command == "c":
        ui_create_account()
    elif command == "i":
        ui_login()
    elif command == "o":
        ui_logout()
    elif command == "p":
        print_help()
    elif command == "q":
        exit_program()
    # Files
    elif command == "d":
        ui_download()
    elif command == "l":
        ui_listfile()
    elif command == "r":
        ui_delete()
    elif command == "s":
        ui_share()
    elif command == "u":
        ui_upload()
    # Unknown command
    else:
        print(command+": unknown command")

def handler(signum, frame):
    """
    Signal handler handling Ctrl+C event.
    """
    print("\nReceived signal: ", signum)
    print("Exit")
    exit_program()

def exit_program():
    """
    Save the list before exit the program.
    """
    os.system("rm -f *.data")
    if client_conn.is_login():
        filelist.save(password, "salt", mylist)
        client_conn.upload(mylist)
        client_conn.logout()
    print("Bye")
    sys.exit()

def ui_login():
    """
    Handle authentication steps during user login.
    """
    if client_conn.is_login():
        print("You already login")
        return
    # Connect to server
    print("Username: ", end='')
    username = input()
    global password
    password = getpass.getpass('Password: ')
    pw_server = hashlib.sha256()
    pw_server.update(password.encode('UTF-8'))
    status = client_conn.authenticate(username, pw_server.digest())
    # Get filelist
    if status:
        print("Login success")
    else:
        print("Login failure")
        return
    # Download the filelist
    status = client_conn.download(mylist)
    if status:
        # List exist on server and successfuly downloaded
        filelist.load(password, "salt", mylist)
    else:
        # List not exist on server
        pass

def ui_logout():
    """
    Handle the logout events.
    """
    if client_conn.is_login():
        filelist.save(password, "salt", mylist)
        client_conn.upload(mylist)
    status = client_conn.logout()
    filelist.mylist = {}
    if status:
        print("Logout success")
    else:
        print("Logout failure")

def ui_create_account():
    """
    Create an new account.
    """
    print("Username: ", end='')
    global password
    username = input()
    password = getpass.getpass('Password: ')
    pw_server = hashlib.sha256()
    pw_server.update(password.encode('UTF-8'))
    status = client_conn.registrate(username, pw_server.digest())
    if status:
        print("Create account success")
    else:
        print("Create account failure")

def ui_upload():
    """
    Encrypte the file and upload.
    """
    if not client_conn.is_login():
        print("Please login first")
        #return
    print("Filename: ", end='')
    filename = input()
    status = client_conn.upload_file(filename)
    if status:
        print("Upload success")
    else:
        print("Upload failure")

def ui_download():
    if not client_conn.is_login():
        print("Please login first")
        return
    print("Filename: ", end='')
    filename = input()
    print("Save as: ", end='')
    saveas = input()
    status = client_conn.download_file(filename, saveas)
    if status:
        print("Download success")
    else:
        print("Download failure")

def ui_share():
    if not client_conn.is_login():
        print("Please login first")
        return
    # Enter recipient username
    print("Invite people (username): ", end='')
    recipient = input().strip()
    # Recipient's email
    recv_email = None
    print("Recipient's email address: ", end='')
    recv_email = input().strip()

    # Get target's public key
    choice = None
    while choice != "1" and choice != "2":
        print("Obtain the recipent's public key:")
        print(" 1) Download from Hong Kong Post")
        print(" 2) Input from file")
        print("Choice [1,2]: ", end='')
        choice = input().strip()
    public_key = None
    try:
        if choice == "1":
            # Download from HK Post
            public_key = rsa.get_cert(recv_email, True)
        if choice == "2":
            # Import from file
            print("Public key file: ", end='')
            filename = input().strip()
            public_key = rsa.get_cert_from_file(filename)
    except Exception as e:
        log.print_exception(e)
        log.print_error("error", "failed to load cert")
        return 

    # Get user's private key to signoff
    private_key = rsa.load_private_cert_from_file("/home/star/.ssh/me.key.pem2")

    # Encrypt the filelist record
    print("File to share: ", end='')
    filename = input()
    sender = "oneonestar@gmail.com"
    record = filelist.export_record(filename, sender, recv_email, public_key, private_key)
    if record == None:
        print("Failed to share file")
        return
    # Send to server
    client_conn.share(recipient, record)


def ui_listfile():
    if not client_conn.is_login():
        print("Please login first")
        return
    # Get share files
    client_conn.get_share()
    # Listing
    filelist.listing()

def ui_delete():
    if not client_conn.is_login():
        print("Please login first")
        return
    print("Filename: ", end='')
    filename = input()
    record = filelist.get(filename)
    if record:
        client_conn.delete(record['filename_rand'])
    filelist.delete(filename)

if __name__ == "__main__":
    '''
    For testing
    '''
    signal.signal(signal.SIGINT, handler)

    #url = "https://blog.onestar.moe:8080"
    client_conn.setup("http://localhost:8080/", "../server/config/server.pem")

    print("Welcome to ComfortZone - Secure Cloud Storage Service")
    print()
    print()
    while True:
        event_loop()

    # Upload a file
    # List files
    #filelist.listing()
    # Upload filelist
    # Download filelist
    # Download a file
    #client_conn.download_file("testing.txt", "saveas.txt")

    # Logout
    #client_conn.logout()
    #client_conn.download_file("testing.txt", "saveas.txt")
