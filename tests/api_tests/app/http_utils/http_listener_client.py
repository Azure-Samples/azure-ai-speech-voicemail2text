#!/usr/bin/env python
# coding: utf-8
# Copyright (c) Microsoft. All rights reserved.
# Licensed under the MIT license. See LICENSE.md file in the project root for full license information.



import threading
from api_tests.core.socket_utils import get_available_port
from api_tests.core.listeners.http_listeners.http_listeners_server import HTTPListenerServer
import time
from api_tests.core.config_utils import get_config_value
import api_tests.core.server_status_utils as server_status_utils

class HTTPListenerClient:
    listener_host = get_config_value('httptest', 'http_listener_host_local')
    listener_port = get_available_port()

    def __init__(self):
        self.http_listener_server = HTTPListenerServer()
        self.server_thread = None

    def start(self):

        self.server_thread = threading.Thread(target=self.http_listener_server.start_listener,
                                             args=(HTTPListenerClient.listener_host, HTTPListenerClient.listener_port))
        self.server_thread.start()


    def stop(self):
        self.http_listener_server.stop_listener()
        self.server_thread.join()
        time.sleep(5)
        self.http_listener_server.reset_stop_server_flag()

    def has_http_listener_started(self):
        running = True
        return self.query_http_listener_status(running)

    def has_http_listener_stopped(self):
        running = False
        return self.query_http_listener_status(running)

    def query_http_listener_status(self, running):
        name = "HTTP test listener"
        hostname = HTTPListenerClient.listener_host
        port = HTTPListenerClient.listener_port
        timeout = int(get_config_value('common', 'fetch_scrid_from_listener_timeout'))
        return server_status_utils.query_server_status(running, name, hostname, port, timeout)