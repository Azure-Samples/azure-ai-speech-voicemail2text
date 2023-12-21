#!/usr/bin/env python
# coding: utf-8
# Copyright (c) Microsoft. All rights reserved.
# Licensed under the MIT license. See LICENSE.md file in the project root for full license information.


from api_tests.core.config_utils import get_config_value
from api_tests.core.file_utils import get_audio_text
from api_tests.core.assert_utils import validate_http_response, validate_request_ack_status_status_accepted, validate_lid_response
from api_tests.app.http_utils.http_request_sender_to_ic import TranscribeRequestSender
from api_tests.core.constants.repo_constant import RepoConstant
import api_tests.core.listeners.http_listeners.request_handler as request_handler

def test_http_with_lid(test_data):
    response = do_test_http(test_data, test_data['lid_enabled'], test_data['lid_mode'])
    validate_lid_response(test_data, response)
    return response

def test_http(test_data):
    response = do_test_http(test_data)
    return response

def do_test_http(test_data, lid_enabled = "False", lid_mode = "AtStartHighAccuracy"):
    request_ack = send_request(test_data, lid_enabled, lid_mode)

    # Validate response status code
    validate_request_ack_status_status_accepted(request_ack.status_code)

    # Fetch scrid from response header
    scrid = request_ack.headers.get("location")
    import threading
    response_available = threading.Event()
    def response_callback():
        print(f"{scrid} response callback called")
        response_available.set()

    request_handler.add_response_callback(scrid, response_callback)

    timeout=int(get_config_value('common', 'fetch_scrid_from_listener_timeout'))
    signal = response_available.wait(timeout)
    if signal is False:
        raise TimeoutError("Timeout reached. Unable to get response")

    response = request_handler.get_response(scrid)
    # Validate response body
    external_request_id = get_config_value('httptest', 'caller_id')
    validate_http_response(scrid, external_request_id, test_data, response)
    return response

def send_request(test_data, lid_enabled = "False", lid_mode = "AtStartHighAccuracy"):
    audio = get_audio_text(RepoConstant.TESTDATA_AUDIO_REPO_HTTP.value, test_data['audio_file'])
    # POST --> Send request to transcribe audio
    transcribe = TranscribeRequestSender()
    request_ack = transcribe.send_transcribe_request(test_data['language'], test_data['content_encoding'], test_data['content_type'], audio, lid_enabled, lid_mode)

    return request_ack
