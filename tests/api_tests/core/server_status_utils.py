#!/usr/bin/env python
# coding: utf-8
# Copyright (c) Microsoft. All rights reserved.
# Licensed under the MIT license. See LICENSE.md file in the project root for full license information.


import time
from api_tests.core.socket_utils import is_port_status

def query_server_status(running, name, hostname, port, timeout):
    start_time = time.time()

    while True:
        status = is_port_status(hostname, port, check_running=running)
        if running:
            error_message = f"{name} has not started."
        else:
            error_message = f"{name} is still running."

        if status:
            break
        elif time.time() - start_time >= timeout:
            raise TimeoutError(f"Timeout reached. {error_message}")

        time.sleep(1)

    return True