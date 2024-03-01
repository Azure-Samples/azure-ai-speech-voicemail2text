#!/usr/bin/env python
# coding: utf-8
# Copyright (c) Microsoft. All rights reserved.
# Licensed under the MIT license. See LICENSE.md file in the project root for full license information.


import json
import http.server

global response_callbacks
response_callbacks = {}

def add_response_callback(scrid, callback):
    global response_callbacks
    response_callbacks[scrid] = callback

global responses
responses = {}

def get_response_or_default(scrid, default=None):
    global responses
    return responses.get(scrid, default)

def get_response(scrid):
    global responses
    return responses[scrid]

class RequestHandler(http.server.BaseHTTPRequestHandler):

    def do_POST(self):
        # Read the POST request body
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)
        scrid = self.headers['X-Reference']
        print(f"Response Body from IC: {post_data}")
        response = {
            'headers': dict(self.headers),
            'body': json.loads(post_data, strict=False)
        }
        global responses
        responses[scrid] = response
        self.trigger_callback(scrid)
        # Send a response
        self.send_response(200)
        self.send_header('Content-type', 'text/plain')
        self.end_headers()
        self.wfile.write(b'Success')

    def trigger_callback(self, scrid):
        global response_callbacks
        if scrid in response_callbacks:
            response_callbacks[scrid]()