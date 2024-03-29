#!/usr/bin/env python
# coding: utf-8
# Copyright (c) Microsoft. All rights reserved.
# Licensed under the MIT license. See LICENSE.md file in the project root for full license information.

import api_tests.app.local_setup.setup_local_smtp_server as local_smtp_server
import threading, os
import pytest
from api_tests.core.reporter import reporter

@pytest.fixture(scope="module")
def smtp_server_fixture(request):
    setup_local_server =  request.config.getoption("--setup_local_server")

    # Start local smtp server if setup_local_server is true
    if setup_local_server.lower() == "true":
        reporter.report(f"\noption --setup_local_server is {setup_local_server}, starting local smtp server")
        server_thread = threading.Thread(target=local_smtp_server.start_smtp_server_local_using_thread)

        server_thread.start()
        if local_smtp_server.has_local_smtp_server_started():
            reporter.report("====smtp_server_fixture -> LOCAL SMTP SERVER STARTED===")

    # Modify server port to nodeport if setup_local_server is false
    if setup_local_server.lower() == "false":
        #os.environ['httptest_server_url'] = 'https://127.0.0.1'
        os.environ['httptest_server_port'] = "32001"

    yield

    # Stop SMTP server at the end
    if setup_local_server.lower() == "true":
        local_smtp_server.stop_smtp_local_server()
        if local_smtp_server.has_local_smtp_server_stopped():
            reporter.report("===smtp_server_fixture -> LOCAL SMTP SERVER STOPPED===")
        local_smtp_server.reset_smtp_server_thread()