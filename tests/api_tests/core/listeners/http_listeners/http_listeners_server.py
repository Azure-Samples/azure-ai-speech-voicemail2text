#!/usr/bin/env python
# coding: utf-8
# Copyright (c) Microsoft. All rights reserved.
# Licensed under the MIT license. See LICENSE.md file in the project root for full license information.



import http.server
import ssl
import threading
from api_tests.core.listeners.http_listeners.request_handler import RequestHandler
from api_tests.core.config_utils import get_config_value

class HTTPListenerServer:
    # stop_server_flag = False

    def __init__(self):
        self.cert_file = get_config_value("certs", "listener_cert_file")
        self.key_file = get_config_value("certs", "listener_key_file")
        self.client_cert_file = get_config_value("certs", "client_cert_file")
        self.stop_server_flag = False

    def create_ssl_context(self):
        ssl_context = ssl.SSLContext(protocol=ssl.PROTOCOL_TLS_SERVER)
        ssl_context.minimum_version = ssl.TLSVersion.TLSv1_2
        ssl_context.verify_mode = ssl.CERT_REQUIRED
        ssl_context.load_cert_chain(certfile=self.cert_file, keyfile=self.key_file)
        ssl_context.load_verify_locations(cafile=self.client_cert_file)
        return ssl_context

    def start_listener(self,host,port):
        # Create an HTTP server object with custom request handler
        http_server = http.server.HTTPServer((host, port), RequestHandler)
        ssl_context:ssl.SSLContext = self.create_ssl_context()
        http_server.socket = ssl_context.wrap_socket(http_server.socket, server_side=True)

        # Start the server
        server_thread = threading.Thread(target=http_server.serve_forever)
        server_thread.start()
        print(f"===Test HTTP Listener started on host {host} and port {port}===")
        # Wait for the user to stop the server
        try:
            while not self.stop_server_flag:
                pass
        except KeyboardInterrupt:
            pass

        # Stop the server gracefully
        http_server.shutdown()
        http_server.server_close()
        # Wait for the server thread to stop
        server_thread.join()


    def stop_listener(self):
        # Set the stop_server_flag to True to stop the server
        self.stop_server_flag = True

    def reset_stop_server_flag(self):
        # Set the stop_server_flag to True to stop the server
        self.stop_server_flag = False
