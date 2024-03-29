#!/usr/bin/env python
# coding: utf-8
# Copyright (c) Microsoft. All rights reserved.
# Licensed under the MIT license. See LICENSE.md file in the project root for full license information.



import os, sys, typing, traceback
import asyncio
import email
from email.message import EmailMessage
from aiosmtpd.controller import Controller
sys.path.append(os.path.join(os.path.abspath(os.curdir)))
from v2ticlib.logger_utils import log, CONTEXT
import Common.request_handler as request_handler
from Common.request_injestor import RequestInjestor
from Common.Smtp.after_deposit_ack_handler import AfterDepositAckHandler
from v2ticlib import config_utils
from v2ticlib.constants.protocols import SMTP
from v2ticlib.constants.fields import SCRID, DELIVERY_TYPE
from v2ticlib.constants.headers import FROM, TO
from v2ticlib.template_utils import template_utils
import v2ticlib.coroutine_timeout_utils as coroutine_timeout
import v2ticlib.request_utils as request_utils
import v2ticlib.ssl_context_utils as ssl_context_utils
from v2ticlib import header_utils

consume_request_timeout = config_utils.get_consume_request_timeout()
global keep_server_alive
keep_server_alive:bool = True

class SMTPHandler():
    def __init__(self):
        self._config_base = SMTP
        self._injestor = RequestInjestor()
        self._after_deposit_ack_handler = AfterDepositAckHandler()

    def get_property(self, property, literal_eval=False):
        return config_utils.get_property(self._config_base, property, literal_eval=literal_eval)

    def is_after_deposit_ack_enabled(self):
        return template_utils.has_after_deposit_ack_template()

    def get_default_return_code(self):
        return self.get_property('default_return_code')

    def use_mailfrom_on_empty_from_header(self):
        return self.get_property('use_mailfrom_on_empty_from_header', literal_eval=True)

    def use_rcpttos_on_empty_to_header(self):
        return self.get_property('use_rcpttos_on_empty_to_header', literal_eval=True)

    def get_return_code(self, request):
        return_code:str = self.get_default_return_code()
        if template_utils.has_smtp_return_code_template():
            return_code = template_utils.render_smtp_return_code(request)

        return return_code

    async def handle_DATA(self, server, session, envelope):
        initial_request_content:dict = request_utils.generate_initial_request_content()
        initial_request_content[DELIVERY_TYPE] = SMTP
        CONTEXT.set(initial_request_content[SCRID])

        mail_from = envelope.mail_from

        rcpt_tos = envelope.rcpt_tos
        log(f'Received message mail_from: {mail_from} with rctp_tos: {rcpt_tos}')

        try:
            return await coroutine_timeout.timeout_after(self.do_handle_DATA(initial_request_content, mail_from, rcpt_tos, envelope), timeout=consume_request_timeout)
        except Exception as e:
            stack = traceback.format_exc()
            log(f'Timed out processing request: {e} - {stack}')
            return f'455 Timed out processing request - {str(e)}'

    async def do_handle_DATA(self, initial_request_content:dict, mail_from, rcpt_tos, envelope):
        email_message: EmailMessage = email.message_from_bytes(envelope.content)
        headers = header_utils.decode_headers(dict(email_message.items()))

        self.handle_empty_headers(headers, mail_from, rcpt_tos)

        audio_bytes = None
        if email_message.is_multipart():
            audio_bytes = self.parse_multipart_request(email_message)
        else:
            audio_bytes = self.parse_simple_request(email_message)

        try:
            request = self.handle_request(initial_request_content, headers, audio_bytes)
        except Exception as e:
            stack = traceback.format_exc()
            log(f'Error processing request: {e} - {stack}')
            return f'455 Error processing request - {str(e)}'

        return_code = self.get_return_code(request)
        log(f'Returning: {return_code}')
        return return_code

    def handle_empty_headers(self, headers: typing.Mapping[str, str], mail_from:str, rcpt_tos:typing.List[str]):
        if not headers.get(FROM) and self.use_mailfrom_on_empty_from_header():
            log('Using mail_from as From header value')
            headers[FROM] = header_utils.decode_header(mail_from)

        if not headers.get(TO) and self.use_rcpttos_on_empty_to_header():
            log('Using rcpt_tos as To header value')
            headers[TO] = [header_utils.decode_header(rcpt_to) for rcpt_to in rcpt_tos]

    def parse_multipart_request(self, email_message:EmailMessage):
        message_bytes = b''
        for message in email_message.get_payload():
            bytes_data = message.get_payload(decode=True)
            message_bytes = message_bytes + bytes_data
        return message_bytes

    def parse_simple_request(self, email_message:EmailMessage):
        message_payload_type = type(email_message.get_payload())
        message_bytes = None
        if(message_payload_type is str):
            message_bytes = email_message.get_payload(decode=True)
        else:
            raise Exception(f'Unknown payload type {message_payload_type}')
        return message_bytes

    def handle_request(self, metadata:dict, headers: typing.Mapping[str, str], body: bytes):
        request = self._injestor.injest(metadata, headers, body)

        if self.is_after_deposit_ack_enabled():
            asyncio.create_task(self.handle_after_deposit_ack(request))

        asyncio.create_task(self.process_request(request))

        return request

    async def process_request(self, request):
        scrid = request_utils.get_scrid(request)
        CONTEXT.set(scrid)
        await request_handler.process_request(request)

    async def handle_after_deposit_ack(self, request):
        scrid = request_utils.get_scrid(request)
        CONTEXT.set(scrid)
        await self._after_deposit_ack_handler.send_acknowledgement(request)

async def start_smtp_server():
    host = config_utils.get_host()
    port = config_utils.get_port()
    ssl_context = ssl_context_utils.create_server_ssl_context()

    handler = SMTPHandler()
    controller = Controller(handler, hostname=host, port=port, tls_context=ssl_context)
    print(f'SMTP Server Listening On: {host}:{port}')
    controller.start()

    # Keep the server running
    while keep_server_alive:
        await asyncio.sleep(1)

    print('==============Stopping SMTP Server==============')
    controller.stop()

def stop_server():
    global keep_server_alive
    keep_server_alive = False

if __name__ == "__main__":
    asyncio.run(start_smtp_server())
