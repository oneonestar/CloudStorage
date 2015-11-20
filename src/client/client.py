import client_conn
import filelist
import hashlib
import getpass
import signal
import sys

# filename of list
mylist = "list"
password = None


def print_help():
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
    print("  u   upload file")
    print()

def event_loop():
    print()
    print("Command (p for help): ", end="")
    command = input()
    command = command.strip()
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
    elif command == "u":
        ui_upload()
    # Unknown command
    else:
        print(command+": unknown command")

def handler(signum, frame):
    print("\nReceived signal: ", signum)
    print("Exit")
    exit_program()

def exit_program():
    if client_conn.is_login():
        filelist.save(password, "salt", mylist)
        client_conn.upload(mylist)
        client_conn.logout()
    print("Bye")
    sys.exit()

def ui_login():
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
    status = client_conn.download(mylist)
    if status:
        # List exist on server and successfuly downloaded
        filelist.load(password, "salt", mylist)
    else:
        # List not exist on server
        pass

def ui_logout():
    if client_conn.is_login():
        filelist.save(password, "salt", mylist)
        client_conn.upload(mylist)
    status = client_conn.logout()
    if status:
        print("Logout success")
    else:
        print("Logout failure")

def ui_create_account():
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

def ui_listfile():
    if not client_conn.is_login():
        print("Please login first")
        return
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
