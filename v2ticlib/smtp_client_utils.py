#!/usr/bin/env python
# coding: utf-8
# Copyright (c) Microsoft. All rights reserved.
# Licensed under the MIT license. See LICENSE.md file in the project root for full license information.



import email
from email.message import EmailMessage
from email.header import Header
import email.message
from aiosmtplib import SMTP
from v2ticlib.logger_utils import log
import v2ticlib.ssl_context_utils as ssl_context_utils
import v2ticlib.constants.headers as Constants
import v2ticlib.config_utils as config_utils

def get_default_response_encoding() -> str:
     return config_utils.get_property('smtp', Constants.DEFAULT_RESPONSE_ENCODING)

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
     msg = email.message.Message()
     for key, value in headers.items():
          val:str = value
          if val.isascii():
               msg[key] = value
          else:
               header = Header(value, get_default_response_encoding())
               msg[key] = header

     if content is not None:
          msg.set_payload(content)

     return msg