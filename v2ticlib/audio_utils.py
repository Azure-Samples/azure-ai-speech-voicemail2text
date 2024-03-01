#!/usr/bin/env python
# coding: utf-8
# Copyright (c) Microsoft. All rights reserved.
# Licensed under the MIT license. See LICENSE.md file in the project root for full license information.

from base64 import b64encode, b64decode, encodebytes

def encode_audio_bytes(audio_bytes:bytes):
    return str(encodebytes(audio_bytes), 'ascii')

def get_audio_bytes(body:bytes):
    if is_base64_encoded(body):
        return b64decode(body)
    else:
        return body

def is_base64_encoded(body:bytes):
    try:
        str_body = str(body, 'ascii')
        str_stripped_body = str_body.replace('\n', '').replace('\r', '')
        stripped_body = str.encode(str_stripped_body, 'ascii')
        decoded = b64decode(stripped_body)
        encoded = b64encode(decoded)
        return encoded == stripped_body
    except Exception:
        return False
