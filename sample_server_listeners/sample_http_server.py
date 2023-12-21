#!/usr/bin/env python
# coding: utf-8
# Copyright (c) Microsoft. All rights reserved.
# Licensed under the MIT license. See LICENSE.md file in the project root for full license information.



from http.server import BaseHTTPRequestHandler, HTTPServer
import os, socket
from http import HTTPStatus
import ssl

class SimpleHTTPRequestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(HTTPStatus.OK)
        self.end_headers()
        response_text = 'Hello, GET request received!'
        self.wfile.write(response_text.encode())

    def do_POST(self):
        self.print_response()

    def do_PUT(self):
        self.print_response()

    def print_response(self):
        try:
            if self.path == '/response':
                print("-----------------------")
                print("Received Response:")
                content_length = int(self.headers['Content-Length'])
                self.print_response_headers()
                post_data = self.rfile.read(content_length)
                charset = self.headers.get_content_charset(failobj="utf-8")
                response_str = post_data.decode(encoding=charset)
                print(f'Message Content:{os.linesep}{response_str}')
        except Exception as ex:
            print(f'Exception occurred while handling response:{str(ex)}')
        finally:
            self.send_response(HTTPStatus.OK)
            self.end_headers()

    def print_response_headers(self):
        for header in self.headers.items():
            header_name = header[0]
            header_value = header[1]
            print(f'{header_name}: {header_value}')

def create_ssl_context():
    ssl_context = ssl.SSLContext(protocol=ssl.PROTOCOL_TLS_SERVER)
    ssl_context.minimum_version = ssl.TLSVersion.TLSv1_2
    ssl_context.verify_mode = ssl.CERT_REQUIRED
    ssl_context.load_cert_chain(certfile='etc/certs/listener/certificate.pem', keyfile='etc/certs/listener/private_key.pem')
    ssl_context.load_verify_locations(cafile='etc/certs/client/certificate.pem')
    return ssl_context

def run_http():
    hostname = socket.gethostname()
    host = socket.gethostbyname(hostname)
    port = 8443
    server_address = (host, port)
    httpd = HTTPServer(server_address, SimpleHTTPRequestHandler)
    ssl_context:ssl.SSLContext = create_ssl_context()
    httpd.socket = ssl_context.wrap_socket(httpd.socket, server_side=True)
    print(f"HTTPS Server listener running on IP Address: {host}")
    print(f"Listening for responses on https://{host}:{port}/response")
    httpd.serve_forever()

if __name__ == '__main__':
    run_http()