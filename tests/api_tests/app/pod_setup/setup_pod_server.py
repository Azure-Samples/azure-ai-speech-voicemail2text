#!/usr/bin/env python
# coding: utf-8
# Copyright (c) Microsoft. All rights reserved.
# Licensed under the MIT license. See LICENSE.md file in the project root for full license information.



import sys, os
sys.path.append(os.path.join(os.path.abspath(os.curdir)))
import os, time
import subprocess
import threading
from datetime import datetime
from api_tests.core.reporter import reporter
from api_tests.core.config_utils import get_config_value
import api_tests.core.server_status_utils as server_status_utils
from api_tests.core.docker_utils import delete_container_and_image,delete_images
import api_tests.core.config_utils as config_utils
import time

# Define a threading event to signal the HTTP server thread to stop
stop_server_flag = False
server_process = None
test_profile_base_dir="tests/api_tests/resources"

def start_pod_server(deployment_name: str):
    global server_process
    test_quick_start_command = f"make quick_start deployment={deployment_name} base_dir={test_profile_base_dir}"

    # Start the http server
    if os.name == "nt":
        print(f"Starting the pod server using command on windows : {test_quick_start_command}")
        server_process = subprocess.Popen(test_quick_start_command)
    else:
        server_process = subprocess.run(test_quick_start_command, shell=True)

def stop_pod_server(deployment_name: str):
    # Set the stop_event to signal the HTTP server thread to stop
    global stop_server_flag
    stop_server_flag = True

    destroy_out = subprocess.run(f"make destroy_pod deployment={deployment_name}", capture_output=True, shell=True, timeout=60)
    reporter.report(destroy_out)
    clean_out = subprocess.run(f"make clean deployment={deployment_name} base_dir={test_profile_base_dir}", capture_output=True, shell=True, timeout=60)
    reporter.report(clean_out)


def start_pod_server_using_thread(deployment_name: str):
    global stop_server_flag,server_process
    http_server_timeout = config_utils.get_local_server_timeout()
    print(f'Local http server timeout: {http_server_timeout} seconds')

    pod_server_thread = threading.Thread(target=start_pod_server,args=(deployment_name,))
    pod_server_thread.start()

    try:
        timeout_start = time.time()
        while not stop_server_flag:
            if time.time() > timeout_start + http_server_timeout:
                print("Timeout reached while waiting for the local http server to stop. Stopping the server now.")
                break
            pass
    except KeyboardInterrupt:
            pass

    if server_process:
        server_process.terminate()
        server_process.wait()
        server_process = None

def cleanup_pod_server():
    today = datetime.today().date()
    formatted_date = today.strftime("%Y%m%d")

    # Cleanup the pod server
    docker_container_image_prefix = get_config_value('podsetup','docker_container_image_prefix')

    #Cleanup docker container and image if exists
    delete_images(f"{docker_container_image_prefix}{formatted_date}")
