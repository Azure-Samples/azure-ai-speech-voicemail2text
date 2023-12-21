#!/usr/bin/env python
# coding: utf-8
# Copyright (c) Microsoft. All rights reserved.
# Licensed under the MIT license. See LICENSE.md file in the project root for full license information.



import sys, os
import os
import subprocess
import threading
sys.path.append(os.path.join(os.path.abspath(os.curdir)))
from api_tests.core.reporter import reporter
from api_tests.core.config_utils import get_config_value
import api_tests.core.server_status_utils as server_status_utils

# Define a threading event to signal the HTTP server thread to stop
stop_server_flag = False
smtp_server_process = None

def start_smtp_local_server():
    global smtp_server_process

    # Set the smtp server config in enviornment variable
    os.environ['profiles_folder'] = 'etc/profiles/sample_smtp'
    os.environ['profiles_profile'] = 'etc.profiles.sample_smtp.profile.SampleSmtpProfile'

    # Start the smtp server
    smtp_server_process = subprocess.Popen(["python", "./servers/smtp_server.py"])

def reset_smtp_server_thread():
    # Set the stop_event to signal the HTTP server thread to stop
    global stop_server_flag
    stop_server_flag = False

def stop_smtp_local_server():
    # Set the stop_event to signal the HTTP server thread to stop
    global stop_server_flag
    stop_server_flag = True

    # Reset the environment variables
    os.unsetenv('profiles_folder')
    os.unsetenv('profiles_profile')

def start_smtp_server_local_using_thread():
    global stop_server_flag,smtp_server_process

    smtp_server_thread = threading.Thread(target=start_smtp_local_server)
    smtp_server_thread.start()

    try:
        while not stop_server_flag:
            pass
    except KeyboardInterrupt:
            pass

    smtp_server_thread.join()
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
    hostname = 'localhost'
    port = int(get_config_value('smtptest', 'smtp_server_port'))
    timeout = int(get_config_value('common', 'fetch_scrid_from_listener_timeout'))
    return server_status_utils.query_server_status(running, name, hostname, port, timeout)