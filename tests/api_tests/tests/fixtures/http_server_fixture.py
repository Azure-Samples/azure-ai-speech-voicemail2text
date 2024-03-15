#!/usr/bin/env python
# coding: utf-8
# Copyright (c) Microsoft. All rights reserved.
# Licensed under the MIT license. See LICENSE.md file in the project root for full license information.

import pytest, os
import api_tests.app.local_setup.setup_local_http_server as local_http_server
import threading
from api_tests.core.reporter import reporter

@pytest.fixture(scope="module")
def http_server_fixture(request):
    setup_local_server =  request.config.getoption("--setup_local_server")

    # Start local http server if setup_local_server is true
    if setup_local_server.lower() == "true":
        reporter.report(f"\noption --setup_local_server is {setup_local_server}, starting local http server")
        server_thread = threading.Thread(target=local_http_server.start_http_server_local_using_thread)

        server_thread.start()
        if local_http_server.has_local_http_server_started():
            reporter.report("===http_server_fixture -> LOCAL HTTP SERVER STARTED===")

    yield

    # Stop local http server if setup_local_server is true
    if setup_local_server.lower() == "true":
        local_http_server.stop_http_local_server()
        if local_http_server.has_local_http_server_stopped():
            reporter.report("===http_server_fixture -> LOCAL HTTP SERVER STOPPED===")
        local_http_server.reset_http_server_thread()