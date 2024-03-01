#!/usr/bin/env python
# coding: utf-8
# Copyright (c) Microsoft. All rights reserved.
# Licensed under the MIT license. See LICENSE.md file in the project root for full license information.

import threading
import api_tests.app.utils.header_utils as header_utils
from api_tests.core.file_utils import get_audio_text
from api_tests.app.smtp_utils.smtp_email_sender_to_ic import send_email_with_audio
from api_tests.core.assert_utils import validate_smtp_response, validate_request_ack_status_status_smtp_request, validate_after_deposit_ack_smtp_request
import api_tests.core.listeners.smtp_listeners.smtp_listener as smtp_listeners
from api_tests.core.config_utils import get_config_value


async def test_smtp(test_data, after_deposit_ack_validate = False):
    response = await do_test_smtp(test_data, after_deposit_ack_validate)
    return response

async def do_test_smtp(test_data, after_deposit_ack_validate = False):
    request_ack:str = await send_request(test_data)
    request_ack_parts = request_ack.split(':')
    request_ack_status = request_ack_parts[0]
    scrid = request_ack_parts[1]
    validate_request_ack_status_status_smtp_request(request_ack_status)

    if after_deposit_ack_validate:
        after_deposit_ack_response = get_after_deposit_ack_or_timeout(scrid)
        validate_after_deposit_ack_smtp_request(after_deposit_ack_response)

    response = get_response_or_timeout(scrid)

    return response

def get_after_deposit_ack_or_timeout(scrid):
    response_available = threading.Event()
    def response_callback():
        print(f"{scrid} response callback called")
        response_available.set()

    smtp_listeners.add_after_deposit_ack_callback(scrid, response_callback)

    timeout=int(get_config_value('common', 'fetch_scrid_from_listener_timeout'))
    signal = response_available.wait(timeout)
    if signal is False:
        raise TimeoutError("Timeout reached. Unable to get response")

    response = smtp_listeners.get_after_deposit_ack_response(scrid)
    return response

def get_response_or_timeout(scrid):
    response_available = threading.Event()
    def response_callback():
        print(f"{scrid} response callback called")
        response_available.set()

    smtp_listeners.add_response_callback(scrid, response_callback)

    timeout=int(get_config_value('common', 'fetch_scrid_from_listener_timeout'))
    signal = response_available.wait(timeout)
    if signal is False:
        raise TimeoutError("Timeout reached. Unable to get response")

    response = smtp_listeners.get_response(scrid)
    return response

async def send_request(test_data):
    smtp_headers = header_utils.get_smtp_default_headers()

    headers = header_utils.create_headers(test_data, smtp_headers)

    content = get_audio_text(test_data['audio_file'])

    request_ack:str = await send_email_with_audio(test_data, headers, content)
    return request_ack

def validate_success_smtp_response(test_data, response):
    validate_smtp_response(test_data, response)