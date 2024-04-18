#!/usr/bin/env python
# coding: utf-8
# Copyright (c) Microsoft. All rights reserved.
# Licensed under the MIT license. See LICENSE.md file in the project root for full license information.

from email.message import Message
from email.header import Header
from email.header import decode_header as email_decode_header
import v2ticlib.json_utils as json_utils
import typing

def encode_header(header_value:str, encoding:str='utf-8') -> str:
    header = Header(header_value, encoding)
    message = Message()
    message['header_name'] = header
    string_message = message.as_string()
    return string_message.split(':')[1].strip()

def decode_header(header: Header) -> str:
    if header is None:
        return None
    final_header_value = ''
    header_tuple_list = email_decode_header(header)
    for header_tuple in header_tuple_list:
        header_value = header_tuple[0]
        encoding = header_tuple[1]
        if type(header_value) is str:
            final_header_value += header_value
            continue
        if encoding is None:
            encoding = 'utf-8'
        final_header_value += header_value.decode(encoding)
    return final_header_value

def decode_headers(headers:dict) -> str:
    decoded_headers = {}
    for key, value in headers.items():
        if value is not None:
            header_value = decode_header(value)
            decoded_headers[key] = header_value
    return decoded_headers

def update_headers_with_escaped_values(headers:typing.Mapping[str, str]):
    return json_utils.update_json_values(headers)