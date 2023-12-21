#!/usr/bin/env python
# coding: utf-8
# Copyright (c) Microsoft. All rights reserved.
# Licensed under the MIT license. See LICENSE.md file in the project root for full license information.



import sys, os
sys.path.append(os.path.join(os.path.abspath(os.curdir)))
import os
import subprocess
import threading
from api_tests.core.reporter import reporter
from api_tests.core.config_utils import get_config_value
import api_tests.core.server_status_utils as server_status_utils

# Define a threading event to signal the HTTP server thread to stop
stop_server_flag = False
http_server_process = None

def start_http_local_server():
    global http_server_process
    # Set the http server config in enviornment variable
    os.environ['profiles_folder'] = get_config_value('httptest', 'http_test_profiles_folder_local')
    os.environ['profiles_profile'] = get_config_value('httptest', 'http_test_profiles_profile_local')

    # Start the http server
    http_server_process = subprocess.Popen(["python", "./servers/https_server.py"])

def stop_http_local_server():
    # Set the stop_event to signal the HTTP server thread to stop
    global stop_server_flag
    stop_server_flag = True

    # Reset the environment variables
    os.unsetenv('profiles_folder')
    os.unsetenv('profiles_profile')

def reset_http_server_thread():
    # Set the stop_event to signal the HTTP server thread to stop
    global stop_server_flag
    stop_server_flag = False

def start_http_server_local_using_thread():
    global stop_server_flag,http_server_process

    http_server_thread = threading.Thread(target=start_http_local_server)
    http_server_thread.start()

    try:
        while not stop_server_flag:
            pass
    except KeyboardInterrupt:
            pass

    http_server_thread.join()
    if http_server_process:
        http_server_process.terminate()
        http_server_process.wait()
        http_server_process = None

def has_local_http_server_started():
    running = True
    return query_local_http_server_status(running)

def has_local_http_server_stopped():
    running = False
    return query_local_http_server_status(running)

def query_local_http_server_status(running):
    name = "Local HTTP server"
    hostname = 'localhost'
    port = int(get_config_value('httptest', 'server_port'))
    timeout = int(get_config_value('common', 'fetch_scrid_from_listener_timeout'))
    return server_status_utils.query_server_status(running, name, hostname, port, timeout)