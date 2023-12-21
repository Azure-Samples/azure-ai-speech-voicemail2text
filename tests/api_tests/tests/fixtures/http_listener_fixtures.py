#!/usr/bin/env python
# coding: utf-8
# Copyright (c) Microsoft. All rights reserved.
# Licensed under the MIT license. See LICENSE.md file in the project root for full license information.

import pytest
from api_tests.app.http_utils.http_listener_client import HTTPListenerClient
import api_tests.app.local_setup.setup_local_http_server as local_http_server
import threading
from api_tests.core.reporter import reporter

@pytest.fixture(scope="module")
def http_listener_fixture(request):
    setup_local_server =  request.config.getoption("--setup_local_server")

    # Start local http server if setup_local_server is true
    if setup_local_server.lower() == "true":
        reporter.report(f"\noption --setup_local_server is {setup_local_server}, starting local http server")
        server_thread = threading.Thread(target=local_http_server.start_http_server_local_using_thread)

        server_thread.start()
        if local_http_server.has_local_http_server_started():
            reporter.report("===http_listener_fixture -> LOCAL HTTP SERVER STARTED===")


    # Create HTTP Listener client
    http_listener_client = HTTPListenerClient()
    # Start HTTP Listener server at the start
    http_listener_client.start()
    if http_listener_client.has_http_listener_started():
        reporter.report("===http_listener_fixture -> HTTP TEST LISTENER STARTED====")

    yield

    # Stop local http server if setup_local_server is true
    if setup_local_server.lower() == "true":
        local_http_server.stop_http_local_server()
        if local_http_server.has_local_http_server_stopped():
            reporter.report("===http_listener_fixture -> LOCAL HTTP SERVER STOPPED===")
        local_http_server.reset_http_server_thread()

    # Stop HTTP Listener server at the end
    http_listener_client.stop()
    if http_listener_client.has_http_listener_stopped():
        reporter.report("===http_listener_fixture -> HTTP TEST LISTENER STOPPED===")