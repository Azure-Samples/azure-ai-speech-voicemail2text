#!/usr/bin/env python
# coding: utf-8
# Copyright (c) Microsoft. All rights reserved.
# Licensed under the MIT license. See LICENSE.md file in the project root for full license information.



import ssl
from aiosmtplib import SMTP
from api_tests.core.config_utils import get_config_value


def create_ssl_context():
    client_cert_file = get_config_value("certs", "client_cert_file")
    client_key_file = get_config_value("certs", "client_key_file")
    server_cert_file = get_config_value("certs", "server_cert_file")
    ssl_context = ssl.SSLContext(protocol=ssl.PROTOCOL_TLS_CLIENT)
    ssl_context.minimum_version = ssl.TLSVersion.TLSv1_2
    ssl_context.load_cert_chain(certfile=client_cert_file, keyfile=client_key_file)
    ssl_context.load_verify_locations(cafile=server_cert_file)
    return ssl_context


async def send_email(sender_email:str, receiver_email:str, message):
    smtp_server = get_config_value('smtptest', 'smtp_server_url')
    smtp_port = get_config_value('smtptest', 'smtp_server_port')
    ssl_context = create_ssl_context()
    timeout=int(get_config_value('common', 'fetch_scrid_from_listener_timeout'))
    smtp = SMTP(hostname=smtp_server, port=smtp_port, tls_context=ssl_context, start_tls=True)
    await smtp.connect()
    request_ack = await smtp.send_message(message, sender=sender_email, recipients=receiver_email, timeout=timeout)
    await smtp.quit()

    print(f"Acknowledgement after sending mail: {request_ack}")

    return request_ack
