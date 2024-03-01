#!/usr/bin/env python
# coding: utf-8
# Copyright (c) Microsoft. All rights reserved.
# Licensed under the MIT license. See LICENSE.md file in the project root for full license information.

import argparse
import os
import asyncio
import ssl
from email.mime.text import MIMEText
from aiosmtplib import SMTP

def create_ssl_context():
    ssl_context = ssl.SSLContext(protocol=ssl.PROTOCOL_TLS_CLIENT)
    ssl_context.minimum_version = ssl.TLSVersion.TLSv1_2
    ssl_context.load_cert_chain(certfile='etc/certs/client/certificate.pem', keyfile='etc/certs/client/private_key.pem')
    ssl_context.load_verify_locations(cafile='etc/certs/certificate.pem')
    return ssl_context

async def send_email_with_audio_attachment(host, port):
    # Email configuration
    mail_from = 'sender@example.com'
    rcpt_to = ['receiver1@example.com', 'receiver2@example.com']

    smtp_server = host
    smtp_port = port

    #Start adding headers
    headers = {
        "Message-Id": "20230519004356-epsvaibhav-4130-91405",
        "X-Reference": "20230519004356-epsvaibhav-4130-91405",
        "Reply-To": "replyto@nuance.com",
        "callingNumberWithheld": "False",
        "X-Language": "en-US",
        "Subject": "Test email",
        "Delivered-To": "193967777",
        "From": "11111111",
        "respondWithAudio": "False",
        "Content-Transfer-Encoding": "base64",
        #"To": rcpt_to
    }
    content = None
    # Attach audio file
    with open("etc/audio/sample-audio-en-US-short.wav", "rb") as f:
        import base64
        content = str(base64.encodebytes(f.read()), 'ascii')

    ssl_context = create_ssl_context()
    # Send the email
    smtp_client = SMTP(hostname=smtp_server, port=smtp_port, tls_context=ssl_context, start_tls=True)
    async with smtp_client:
        print(f'smtp email server connected successfully : {smtp_client.hostname}:{smtp_client.port}')
        message = MIMEText("email")
        for k,v in headers.items():
            message.add_header(k, v)

        #Below is an example of how to set header values with special characters like double quotes (")
        #from email.header import Header
        #message['From'] = Header('"1234567" <sender@example.com>', 'utf-8')

        message.set_payload(content)

        return_tuple = await smtp_client.send_message(message, sender=mail_from, recipients=rcpt_to)
        print(return_tuple)
        print(f'return code: {return_tuple[1]}')

# Run the email sending coroutine
if os.name == 'nt':
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

argParser = argparse.ArgumentParser()
argParser.add_argument("--host", type=str, help="hostname", default="smtp-server.v2tic.com", required=False)
argParser.add_argument("--port", type=int, help="port", default=9443, required=False)

args = argParser.parse_args()
print("args=%s" % args)

asyncio.run(send_email_with_audio_attachment(args.host, args.port))

print("Done")