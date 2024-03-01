#!/usr/bin/env python
# coding: utf-8
# Copyright (c) Microsoft. All rights reserved.
# Licensed under the MIT license. See LICENSE.md file in the project root for full license information.


import threading
from api_tests.core.config_utils import get_config_value
from api_tests.core.file_utils import get_audio_text
from api_tests.core.assert_utils import validate_http_response, validate_request_ack_status_status_accepted, validate_external_request_id
from api_tests.app.http_utils.http_request_sender_to_ic import TranscribeRequestSender
import api_tests.core.listeners.http_listeners.request_handler as request_handler
import api_tests.app.utils.header_utils as header_utils


def test_http(test_data):
    response = do_test_http(test_data)
    return response

def do_test_http(test_data):
    request_ack = send_request(test_data)

    # Validate response status code
    validate_request_ack_status_status_accepted(request_ack.status_code)

    # Fetch scrid from response header
    scrid = request_ack.headers.get("location")
    response = get_response_or_timeout(scrid)

    return response

def get_response_or_timeout(scrid):
    response_available = threading.Event()
    def response_callback():
        print(f"{scrid} response callback called")
        response_available.set()

    request_handler.add_response_callback(scrid, response_callback)

    timeout=int(get_config_value('common', 'fetch_scrid_from_listener_timeout'))
    signal = response_available.wait(timeout)
    if signal is False:
        # last check in case the response was received after callback was registered.
        response = request_handler.get_response_or_default(scrid, default=None)
        if response is not None:
            print(f'Got response for scrid {scrid} from listener after timeout')
            return response
        raise TimeoutError("Timeout reached. Unable to get response")

    response = request_handler.get_response(scrid)
    return response

def send_request(test_data):
    http_headers = {
        "X-Caller": get_config_value('httptest', 'caller'),
        "X-Reference": get_config_value('httptest', 'caller_id')
    }
    headers = header_utils.create_headers(test_data, http_headers)
    audio = get_audio_text(test_data['audio_file'])

    transcribe = TranscribeRequestSender()
    request_ack = transcribe.send_transcribe_request(headers, audio)

    return request_ack

def valiate_success_external_request_id(response):
    external_request_id = get_config_value('httptest', 'caller_id')
    response_dict = response['body']
    validate_external_request_id(external_request_id, response_dict['externalRequestID'])

def validate_success_http_response(test_data, response):
    valiate_success_external_request_id(response)
    validate_http_response(test_data, response)