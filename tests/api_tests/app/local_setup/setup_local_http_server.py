#!/usr/bin/env python
# coding: utf-8
# Copyright (c) Microsoft. All rights reserved.
# Licensed under the MIT license. See LICENSE.md file in the project root for full license information.



import sys, os
sys.path.append(os.path.join(os.path.abspath(os.curdir)))
import subprocess
import threading
from api_tests.core.reporter import reporter
from api_tests.core.config_utils import get_config_value
import api_tests.core.server_status_utils as server_status_utils
from api_tests.core.env_utils import set_os_env, unset_os_env
import api_tests.core.config_utils as config_utils
import time


# Define a threading event to signal the HTTP server thread to stop
stop_server_flag = False
http_server_process = None
keep_printing_logs = True
server = False

def start_http_local_server():
    global http_server_process,server, keep_printing_logs

    # Start the http server
    http_server_process = subprocess.Popen(["python", "./servers/https_server.py"], stdout=subprocess.PIPE, text=True)

    while keep_printing_logs:
        server_log = http_server_process.stdout.readline()
        if not server_log:
            break
        print(server_log)

def stop_http_local_server():
    # Set the stop_event to signal the HTTP server thread to stop
    global stop_server_flag, keep_printing_logs
    stop_server_flag = True
    keep_printing_logs = False

def reset_http_server_thread():
    # Set the stop_event to signal the HTTP server thread to stop
    global stop_server_flag, keep_printing_logs
    stop_server_flag = False
    keep_printing_logs = True

def start_http_server_local_using_thread():
    global stop_server_flag,http_server_process
    http_server_timeout = config_utils.get_local_server_timeout()
    print(f'Local http server timeout: {http_server_timeout} seconds')

    # Set the environment variables for http server profiles
    reporter.report("===start_http_local_server -> Setting up os.environ() for http server profiles fixture====")
    set_os_env('profiles_folder', get_config_value('httptest', 'http_test_profiles_folder_local'))
    set_os_env('profiles_profile', get_config_value('httptest', 'http_test_profiles_profile_local'))

    http_server_thread = threading.Thread(target=start_http_local_server)
    http_server_thread.start()

    try:
        timeout_start = time.time()
        while not stop_server_flag:
            if time.time() > timeout_start + http_server_timeout:
                print("Timeout reached while waiting for the local http server to stop. Stopping the server now.")
                break
            pass
    except KeyboardInterrupt:
            pass

    # Reset the environment variables for http server profiles
    reporter.report("===stop_http_local_server -> Tearing down os.environ() for http server profiles fixture====")
    unset_os_env('profiles_folder')
    unset_os_env('profiles_profile')

    # Terminate the http server process
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
    server_url = get_config_value('httptest', 'server_url')
    hostname = server_url.split('//')[1]
    port = int(get_config_value('httptest', 'server_port'))
    timeout = int(get_config_value('common', 'fetch_scrid_from_listener_timeout'))
    return server_status_utils.query_server_status(running, name, hostname, port, timeout)