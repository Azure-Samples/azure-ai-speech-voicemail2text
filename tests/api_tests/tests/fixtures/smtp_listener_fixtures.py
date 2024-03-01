#!/usr/bin/env python
# coding: utf-8
# Copyright (c) Microsoft. All rights reserved.
# Licensed under the MIT license. See LICENSE.md file in the project root for full license information.



from aiosmtpd.controller import Controller
from api_tests.core.listeners.smtp_listeners.smtp_listener import SimpleSMTPRequestHandler
from api_tests.core.config_utils import get_config_value
import pytest
from api_tests.core.reporter import reporter
import ssl

def create_ssl_context():
    cert_file = get_config_value("certs", "listener_cert_file")
    key_file = get_config_value("certs", "listener_key_file")
    client_cert_file = get_config_value("certs", "client_cert_file")
    ssl_context = ssl.SSLContext(protocol=ssl.PROTOCOL_TLS_SERVER)
    ssl_context.minimum_version = ssl.TLSVersion.TLSv1_2
    ssl_context.verify_mode = ssl.CERT_REQUIRED
    ssl_context.load_cert_chain(certfile=cert_file, keyfile=key_file)
    ssl_context.load_verify_locations(cafile=client_cert_file)
    return ssl_context

@pytest.fixture(scope="module")
def smtp_listener_fixture(request):

    # Create SMTP Listener client
    handler = SimpleSMTPRequestHandler()
    host = get_config_value('smtptest', 'smtp_listener_host_local')
    port = get_config_value('smtptest', 'smtp_listener_port')
    ssl_context = create_ssl_context()
    controller = Controller(handler, hostname=host, port=port, tls_context=ssl_context)
    reporter.report(f"===smtp_listener_fixture -> SMTP TEST LISTENER STARTING on host {host} and port {port}===")
    controller.start()
    if handler.has_smtp_listener_started():
        reporter.report("===smtp_listener_fixture -> SMTP TEST LISTENER STARTED===")

    yield

    # Stop SMTP Listener server at the end
    controller.stop()
    if handler.has_smtp_listener_stopped():
        reporter.report("===smtp_listener_fixture -> SMTP TEST LISTENER STOPPED===")
