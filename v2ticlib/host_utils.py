#!/usr/bin/env python
# coding: utf-8
# Copyright (c) Microsoft. All rights reserved.
# Licensed under the MIT license. See LICENSE.md file in the project root for full license information.



import socket
import os

hostname = socket.gethostname()
ip_address = socket.gethostbyname(hostname)
pid = os.getpid()

def get_hostname():
    return hostname

def get_ip_address():
    return ip_address

def get_pid():
    return pid
