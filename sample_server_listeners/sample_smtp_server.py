#!/usr/bin/env python
# coding: utf-8
# Copyright (c) Microsoft. All rights reserved.
# Licensed under the MIT license. See LICENSE.md file in the project root for full license information.



import email
from email.message import EmailMessage
import os, socket
import asyncio
import ssl
from aiosmtpd.controller import Controller

class SimpleSMTPRequestHandler():

    async def handle_DATA(self, server, session, envelope):
        try:
            email_message: EmailMessage = email.message_from_bytes(envelope.content)
            headers = dict(email_message.items())
            print("Received message:")
            print(f'From: {envelope.mail_from}')
            print(f'To: {envelope.rcpt_tos}')
            print("-----------------------")
            envelope_content = envelope.content
            charset_value = self.get_charset(envelope_content, default_charset='utf-8')
            decoded_content = envelope_content.decode(charset_value)
            print(f'Message data:{os.linesep}{decoded_content}')
        except Exception as ex:
            print(f'Exception occurred while handling response:{ex}')

        return "250 OK"

    def get_charset(self, envelope_content: bytes, default_charset='utf-8'):
        email_message:EmailMessage = email.message_from_bytes(envelope_content)
        print(f'is multi-part: {email_message.is_multipart()}')
        charset_value = email_message.get_content_charset()
        print(f'Retrieved charset from envelope content: {charset_value}')
        if charset_value is None:
            charset_value = default_charset
        return charset_value

def create_ssl_context():
    ssl_context = ssl.SSLContext(protocol=ssl.PROTOCOL_TLS_SERVER)
    ssl_context.minimum_version = ssl.TLSVersion.TLSv1_2
    ssl_context.verify_mode = ssl.CERT_REQUIRED
    ssl_context.load_cert_chain(certfile='etc/certs/listener/certificate.pem', keyfile='etc/certs/listener/private_key.pem')
    ssl_context.load_verify_locations(cafile='etc/certs/client/certificate.pem')
    return ssl_context

async def run_smtp_server():
    hostname = socket.gethostname()
    host = socket.gethostbyname(hostname)
    port = 9025

    handler = SimpleSMTPRequestHandler()
    ssl_context = create_ssl_context()
    controller = Controller(handler, hostname=host, port=port, tls_context=ssl_context)
    controller.start()
    print(f"SMTP Server listener running on IP Address: {host}")
    print(f"Listening for responses on {host}:{port}")

    # Keep the server running
    while True:
        await asyncio.sleep(1)

if __name__ == "__main__":
    asyncio.run(run_smtp_server())