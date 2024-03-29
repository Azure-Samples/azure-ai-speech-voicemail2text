#!/usr/bin/env python
# coding: utf-8
# Copyright (c) Microsoft. All rights reserved.
# Licensed under the MIT license. See LICENSE.md file in the project root for full license information.

import pytest, os, time
from api_tests.app.http_utils.http_listener_client import HTTPListenerClient
from api_tests.core.reporter import reporter

@pytest.fixture(scope="module")
def http_listener_fixture(request):

    # Create HTTP Listener client
    http_listener_client = HTTPListenerClient()
    # Start HTTP Listener server at the start
    http_listener_client.start()
    if http_listener_client.has_http_listener_started():
        reporter.report("===http_listener_fixture -> HTTP TEST LISTENER STARTED====")


    yield

    # Stop HTTP Listener server at the end
    http_listener_client.stop()
    if http_listener_client.has_http_listener_stopped():
        reporter.report("===http_listener_fixture -> HTTP TEST LISTENER STOPPED===")