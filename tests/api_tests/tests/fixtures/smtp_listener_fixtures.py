#!/usr/bin/env python
# coding: utf-8
# Copyright (c) Microsoft. All rights reserved.
# Licensed under the MIT license. See LICENSE.md file in the project root for full license information.



from aiosmtpd.controller import Controller
from api_tests.core.listeners.smtp_listeners.smtp_listener import SimpleSMTPRequestHandler
from api_tests.core.config_utils import get_config_value
import api_tests.app.local_setup.setup_local_smtp_server as local_smtp_server
import threading
import pytest
from api_tests.core.reporter import reporter
import ssl

def create_ssl_context():
    cert_dir = get_config_value("certs", "certs_dir")
    client_certificate = 'etc/certs/listener/certificate.pem'#cert_dir + get_config_value("certs", "listener_certificate")
    client_private_key = 'etc/certs/listener/private_key.pem'#cert_dir + get_config_value("certs", "listener_private_key")
    listener_ca_certs = 'etc/certs/client/certificate.pem'#cert_dir + get_config_value("certs", "listener_https_ca_certs")
    ssl_context = ssl.SSLContext(protocol=ssl.PROTOCOL_TLS_SERVER)
    ssl_context.minimum_version = ssl.TLSVersion.TLSv1_2
    ssl_context.verify_mode = ssl.CERT_REQUIRED
    ssl_context.load_cert_chain(certfile=client_certificate, keyfile=client_private_key)
    ssl_context.load_verify_locations(cafile=listener_ca_certs)
    return ssl_context

@pytest.fixture(scope="module", autouse=True)
def smtp_listener_fixture(request):
    setup_local_server =  request.config.getoption("--setup_local_server")

    # Start local smtp server if setup_local_server is true
    if setup_local_server.lower() == "true":
        reporter.report(f"\noption --setup_local_server is {setup_local_server}, starting local smtp server")
        server_thread = threading.Thread(target=local_smtp_server.start_smtp_server_local_using_thread)

        server_thread.start()
        if local_smtp_server.has_local_smtp_server_started():
            reporter.report("====smtp_listener_fixture -> LOCAL SMTP SERVER STARTED===")

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

    yield handler

    # Stop SMTP server at the end
    if setup_local_server.lower() == "true":
        local_smtp_server.stop_smtp_local_server()
        if local_smtp_server.has_local_smtp_server_stopped():
            reporter.report("===smtp_listener_fixture -> LOCAL SMTP SERVER STOPPED===")
        local_smtp_server.reset_smtp_server_thread()

    # Stop SMTP Listener server at the end
    controller.stop()
    if handler.has_smtp_listener_stopped():
        reporter.report("===smtp_listener_fixture -> SMTP TEST LISTENER STOPPED===")

def get_smtp_default_headers():
    headers = {
        "Message-Id": "Nuance V2T Conversion",
        "X-Reference": "20230519004356-epsvaibhav-4130-91405",
        "Reply-To": "replyto@nuance.com",
        "callingNumberWithheld": "False",
        "Subject": "Test email",
        "Delivered-To": "193967777",
        "From": "11111111",
        "respondWithAudio": "False",
        "Content-Transfer-Encoding": "base64"
    }

    return headers
