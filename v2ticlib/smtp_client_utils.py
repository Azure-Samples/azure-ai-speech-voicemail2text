#!/usr/bin/env python
# coding: utf-8
# Copyright (c) Microsoft. All rights reserved.
# Licensed under the MIT license. See LICENSE.md file in the project root for full license information.



import email
from email.message import EmailMessage
from aiosmtplib import SMTP
from v2ticlib.logger_utils import log
import v2ticlib.ssl_context_utils as ssl_context_utils
import v2ticlib.constants.constants as Constants

async def send(smtp_sender_host:str, smtp_sender_port:int, mail_from:str, rcpt_to:str, headers:dict, content:bytes, timeout:int) -> str:

     message:EmailMessage = create_email_message(headers, content)

     ssl_context = ssl_context_utils.create_client_ssl_context()
     smtp_client = SMTP(hostname=smtp_sender_host, port=smtp_sender_port, tls_context=ssl_context, start_tls=True, timeout=timeout)
     async with smtp_client:
          response_tuple = await smtp_client.send_message(message, sender=mail_from, recipients=rcpt_to)
          return_code = response_tuple[1]
          log(f'return code: {return_code}')
          return return_code

def create_email_message(headers:dict, content:bytes):
     headers_list = [f'{k}: {v}' for k, v in headers.items()]
     headers_str = Constants.CRLF.join(headers_list) + Constants.CRLF
     mime_document_bytes = headers_str.encode(encoding='ascii')
     if content is not None:
          mime_document_bytes += content

     email_message:EmailMessage = email.message_from_bytes(mime_document_bytes)
     return email_message
