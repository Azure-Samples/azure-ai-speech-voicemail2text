#!/usr/bin/env python
# coding: utf-8
# Copyright (c) Microsoft. All rights reserved.
# Licensed under the MIT license. See LICENSE.md file in the project root for full license information.



import socket

def get_machine_ip():
    try:
        # Create a socket object
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

        # Connect to a remote server (in this case, Google's public DNS server)
        sock.connect(("8.8.8.8", 80))

        # Get the local IP address of the machine
        machine_ip = sock.getsockname()[0]

        # Close the socket
        sock.close()

        return machine_ip
    except socket.error as e:
        print(f"Error: {e}")
        return None


def get_available_port():
    # Create a socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    try:
        # Bind the socket to any available port (port 0)
        sock.bind(('localhost', 0))

        # Get the port number assigned by the operating system
        _, port = sock.getsockname()

        return port
    finally:
        # Close the socket
        sock.close()


def is_port_status(host, port, check_running=True):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(1)  # Set a timeout in seconds

    try:
        sock.connect((host, port))
        return check_running  # Port is running if check_running is True
    except (ConnectionRefusedError, socket.timeout):
        return not check_running  # Port is not running or not reachable if check_running is True
    finally:
        sock.close()