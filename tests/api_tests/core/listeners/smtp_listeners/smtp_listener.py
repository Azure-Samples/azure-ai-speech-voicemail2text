#!/usr/bin/env python
# coding: utf-8
# Copyright (c) Microsoft. All rights reserved.
# Licensed under the MIT license. See LICENSE.md file in the project root for full license information.


import asyncio
import json
import time
import email
from email.message import EmailMessage
from api_tests.core.config_utils import get_config_value
import api_tests.core.server_status_utils as server_status_utils

global response_callbacks
response_callbacks = {}

def add_response_callback(scrid, callback):
    global response_callbacks
    response_callbacks[scrid] = callback

global after_deposit_callbacks
after_deposit_callbacks = {}

def add_after_deposit_ack_callback(scrid, callback):
    global after_deposit_callbacks
    after_deposit_callbacks[scrid] = callback

global responses
responses = {}

global after_conversion_deposit_ack_response
after_conversion_deposit_ack_response = {}

def get_response(scrid):
    global responses
    return responses[scrid]

def get_after_deposit_ack_response(scrid):
    global after_conversion_deposit_ack_response
    return after_conversion_deposit_ack_response[scrid]

class SimpleSMTPRequestHandler():
    def __init__(self):
        self.scrid_dict = {}

    async def handle_DATA(self, server, session, envelope):
        email_message:EmailMessage = self.parse_email(envelope.content)
        headers = {k:v for k,v in email_message.items()}
        scrid = headers['X-Scrid']

        message_payload_type = type(email_message.get_payload())
        message_bytes = None
        if message_payload_type is str:
            message_bytes = email_message.get_payload(decode=True)

        response = {
            'scrid': scrid,
            'headers': headers,
            'email_from': envelope.mail_from,
            'email_to': envelope.rcpt_tos,
            'body': json.loads(message_bytes, strict=False)
        }
        if headers['Subject'] == 'Delivery Notification (Success)':
            print(f"Received after conversion deposit ack response for scrid: {headers['X-Scrid']}")
            global after_conversion_deposit_ack_response
            after_conversion_deposit_ack_response[scrid] = response
            self.trigger_after_deposit_callback(scrid)
        else:
            global responses
            responses[scrid] = response
            self.trigger_callback(scrid)

        return "250 OK"

    def trigger_callback(self, scrid):
        global response_callbacks
        if scrid in response_callbacks:
            response_callbacks[scrid]()

    def trigger_after_deposit_callback(self, scrid):
        global after_deposit_callbacks
        if scrid in after_deposit_callbacks:
            after_deposit_callbacks[scrid]()

    def parse_email(self, envelope_content):
        email_message:EmailMessage = email.message_from_bytes(envelope_content)
        print(f'is multi-part: {email_message.is_multipart()}')
        charset_value = email_message.get_content_charset()
        print(f'Retrieved charset from envelope content: {charset_value}')
        return email_message

    async def get_received_email_details(self,scrid):
        timeout = int(get_config_value('common', 'fetch_scrid_from_listener_timeout'))
        start_time = time.time()

        while True:
            if scrid in self.scrid_dict.keys():
                return self.scrid_dict[scrid]
            elif time.time() - start_time >= timeout:
                raise TimeoutError("Timeout reached. Email response not received.")

            await asyncio.sleep(1)

    def has_smtp_listener_started(self):
        running = True
        return self.query_smtp_listener_status(running)

    def has_smtp_listener_stopped(self):
        running = False
        return self.query_smtp_listener_status(running)

    def query_smtp_listener_status(self, running):
        name = "SMTP test listener"
        hostname = get_config_value('smtptest', 'smtp_listener_host_local')
        port = int(get_config_value('smtptest', 'smtp_listener_port'))
        timeout = int(get_config_value('common', 'fetch_scrid_from_listener_timeout'))
        return server_status_utils.query_server_status(running, name, hostname, port, timeout)