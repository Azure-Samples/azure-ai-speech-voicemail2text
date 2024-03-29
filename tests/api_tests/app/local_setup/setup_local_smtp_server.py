#!/usr/bin/env python
# coding: utf-8
# Copyright (c) Microsoft. All rights reserved.
# Licensed under the MIT license. See LICENSE.md file in the project root for full license information.



import sys, os
import os
import subprocess
import threading
import asyncio
sys.path.append(os.path.join(os.path.abspath(os.curdir)))
from api_tests.core.reporter import reporter
from api_tests.core.config_utils import get_config_value
import api_tests.core.server_status_utils as server_status_utils
from api_tests.core.env_utils import set_os_env, unset_os_env
import api_tests.core.config_utils as config_utils
import time


# Define a threading event to signal the HTTP server thread to stop
stop_server_flag = False
smtp_server_process = None

def start_smtp_local_server():
    global smtp_server_process

    # Start the smtp server
    smtp_server_process = subprocess.Popen(["python", "./servers/smtp_server.py"])


def stop_smtp_local_server():
    # Set the stop_event to signal the HTTP server thread to stop
    global stop_server_flag
    stop_server_flag = True


def reset_smtp_server_thread():
    # Set the stop_event to signal the HTTP server thread to stop
    global stop_server_flag
    stop_server_flag = False


def start_smtp_server_local_using_thread():
    global stop_server_flag,smtp_server_process
    smtp_server_timeout = config_utils.get_local_server_timeout()
    print(f'Local smtp server timeout: {smtp_server_timeout} seconds')

    # Set the smtp server  profiles config in enviornment variable
    reporter.report("===server_env_fixture -> Setting up os.environ() for smtp server profiles fixture====")
    set_os_env('profiles_folder', get_config_value('smtptest', 'smtp_test_profiles_folder_local'))
    set_os_env('profiles_profile', get_config_value('smtptest', 'smtp_test_profiles_profile_local'))

    smtp_server_thread = threading.Thread(target=start_smtp_local_server)
    smtp_server_thread.start()

    try:
        timeout_start = time.time()
        while not stop_server_flag:
            if time.time() > timeout_start + smtp_server_timeout:
                print("Timeout reached while waiting for the local smtp server to stop. Stopping the server now.")
                break
            pass
    except KeyboardInterrupt:
            pass

    # Reset the smtp server  profiles config in enviornment variable
    reporter.report("===server_env_fixture -> Tearing down os.environ() for smtp server profiles fixture====")
    unset_os_env('profiles_folder')
    unset_os_env('profiles_profile')

    # Terminate the smtp server process
    if smtp_server_process:
        smtp_server_process.terminate()
        smtp_server_process.wait()
        smtp_server_process = None


def has_local_smtp_server_started():
    running = True
    return query_local_smtp_server_status(running)

def has_local_smtp_server_stopped():
    running = False
    return query_local_smtp_server_status(running)

def query_local_smtp_server_status(running):
    name = "Local SMTP server"
    hostname = get_config_value('smtptest', 'smtp_server_url')
    port = int(get_config_value('smtptest', 'smtp_server_port'))
    timeout = int(get_config_value('common', 'fetch_scrid_from_listener_timeout'))
    return server_status_utils.query_server_status(running, name, hostname, port, timeout)