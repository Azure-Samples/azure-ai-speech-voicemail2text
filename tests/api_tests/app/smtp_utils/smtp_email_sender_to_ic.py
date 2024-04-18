#!/usr/bin/env python
# coding: utf-8
# Copyright (c) Microsoft. All rights reserved.
# Licensed under the MIT license. See LICENSE.md file in the project root for full license information.



from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from api_tests.core.smtp_utils.smtp_send_email import send_email

async def send_email_with_audio(test_data:dict, headers:dict, content):
    

    message = MIMEMultipart()
    message['From'] = test_data['sender_email']
    message['To'] = ', '.join(test_data['receiver_email'])
    message['Subject'] = 'Test email'
    for k, v in headers.items():
        message.add_header(k, v)

    message.set_payload(content)
    return_tuple = await send_email(test_data['sender_email'], test_data['receiver_email'], message)

    return return_tuple[1]
