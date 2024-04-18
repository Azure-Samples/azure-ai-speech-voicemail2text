#!/usr/bin/env python
# coding: utf-8
# Copyright (c) Microsoft. All rights reserved.
# Licensed under the MIT license. See LICENSE.md file in the project root for full license information.

import argparse
import os
import asyncio
import ssl
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from aiosmtplib import SMTP

def create_ssl_context():
    ssl_context = ssl.SSLContext(protocol=ssl.PROTOCOL_TLS_CLIENT)
    ssl_context.minimum_version = ssl.TLSVersion.TLSv1_2
    ssl_context.load_cert_chain(certfile='etc/certs/client/certificate.pem', keyfile='etc/certs/client/private_key.pem')
    ssl_context.load_verify_locations(cafile='etc/certs/certificate.pem')
    return ssl_context

def add_file_attachment(message, file):
    content = None
    # Attach audio file
    with open(file, "rb") as f:
        import base64
        content = str(base64.encodebytes(f.read()), 'ascii')
        attachment = MIMEBase('application', 'octet-stream')
        attachment.set_payload(content)
        attachment.add_header('Content-Disposition', 'attachment', filename=file.split('/')[-1])
        attachment.add_header('Content-Transfer-Encoding', 'base64')
        message.attach(attachment)

async def send_email_with_audio_attachment(host, port):
    # Email configuration
    mail_from = 'sender@example.com'
    rcpt_to = ['receiver1@example.com', 'receiver2@example.com']

    smtp_server = host
    smtp_port = port

    #Headers dictionary
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
        "X-V2TReply" : "admin001@test-pp-v2t-smtp.test-uone.voip.test.com",
        "X-uOneCallID" : '9193020096|local-cname="=?utf-8?Q?ATP_User=5F9?= =?utf-8?Q?193020096?=";remote-cname="=?utf-8?Q?B_WESTPHAL?="',
        "X-uOneCalledID" : "6503332288",
        "x-test-v2t-verification" : "2.0",
        "x-test-v2t-referenceid" : "0228201153248380chlt-pp-vs-061045664110XP0-0",
        "x-test-service" : "x-test-service",
        "content_type" : 'MULTIPART/Voice-Message; BOUNDARY="Boundary_1712209752"'
    }

    # Create the SSL context
    ssl_context = create_ssl_context()

    # Create the email message
    message = MIMEMultipart()
    message['From'] = mail_from
    message['To'] = ', '.join(rcpt_to)
    message['Subject'] = 'Test email'
    for k,v in headers.items():
        message.add_header(k, v)

    #Below is an example of how to set header values with special characters like double quotes (")
    #from email.header import Header
    #message['From'] = Header('"1234567" <sender@example.com>', 'utf-8')

    add_file_attachment(message, "etc/audio/sample-audio-en-US-short.wav")
    
    # Send the email
    smtp_client = SMTP(hostname=smtp_server, port=smtp_port, tls_context=ssl_context, start_tls=True)
    async with smtp_client:
        print(f'smtp email server connected successfully : {smtp_client.hostname}:{smtp_client.port}')
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