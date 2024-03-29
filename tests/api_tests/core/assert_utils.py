#!/usr/bin/env python
# coding: utf-8
# Copyright (c) Microsoft. All rights reserved.
# Licensed under the MIT license. See LICENSE.md file in the project root for full license information.

import os
import traceback
import re
from api_tests.core.reporter import reporter
from api_tests.core.constants.http_status_code import HttpStatusCode
from api_tests.core.config_utils import get_config_value
from api_tests.core.file_utils import read_from_file

def validate_request_ack_status_bad_request(actual_status_code):
    expected_status_code=HttpStatusCode.BAD_REQUEST.value
    validate(actual_status_code, expected_status_code, 'validate bad http request ack status code')

def validate_request_ack_status_status_accepted(actual_status_code):
    expected_status_code=HttpStatusCode.ACCEPTED.value
    validate(expected_status_code, actual_status_code, 'validate http request ack status code')

def validate_request_ack_status_status_smtp_request(actual_status_code):
    expected_status_code='Message accepted for delivery'
    validate(expected_status_code, actual_status_code, 'validate smtp request ack status code')

def validate_request_ack_status_status_bad_smtp_request(actual_status_code):
    expected_status_code="(455, 'Error processing request - Missing audio')"
    validate(expected_status_code, actual_status_code, 'validate bad smtp request ack status code')

def validate_scrid(expected_scrid, actual_scrid):
    validate(expected_scrid, actual_scrid, 'validate response scrid')

def do_validate_response_status(expected_response_status, actual_response_status):
    validate(expected_response_status, actual_response_status, 'validate response status')

def do_validate_recognition_status(expected_recognition_status, actual_recognition_status):
    validate(expected_recognition_status, actual_recognition_status, 'validate recognition status')

def validate_external_request_id(expected_external_request_id, actual_external_request_id):
    validate(expected_external_request_id, actual_external_request_id, 'validate external request ID')

def validate_rtf(rtf_max, actual_rtf):
    validate_numeric(rtf_max, '>', actual_rtf, 'validate rtf')

def validate_confidence_score(confidence_score_min, actual_confidence_score):
    validate_numeric(confidence_score_min, '<=', actual_confidence_score, 'validate confidence score')

def validate_language(language, actual_language):
    validate(language, actual_language, 'validate response requested languages')

def validate_detected_languages(detected_language, actual_detected_language):
    validate(detected_language, actual_detected_language, 'validate response detected languages')

def validate_lid_enabled(lid_enabled, actual_lid_enabled):
    validate(lid_enabled, actual_lid_enabled, 'validate response lid enabled')

def do_validate_notes(expected_notes, actual_notes):
    validate(expected_notes, actual_notes, 'validate response notes')

def validate_notes(test_data, response):
    response_dict = response['body']
    actual_notes = response_dict.get('notes')
    assert actual_notes is not None
    do_validate_notes(test_data['notes'], actual_notes)

def validate_response_status(test_data, response):
    expected_response_status = test_data['status']
    response_dict = response['body']
    actual_response_status = response_dict.get('reasonStatus')
    do_validate_notes(expected_response_status, actual_response_status)

def validate_recognition_status(test_data, response):
    expected_recognition_status = test_data['recognition_status']
    response_dict = response['body']
    actual_recognition_status = response_dict.get('recognitionStatus')
    do_validate_recognition_status(expected_recognition_status, actual_recognition_status)

def validate_http_response(test_data, response):
    response_dict = response['body']
    headers:dict = response['headers']
    validate_response_status(test_data, response)
    do_validate_recognition_status(test_data['recognition_status'], response_dict['recognitionStatus'])
    validate_rtf(test_data['rtf_max'], headers.get('X-RTF'))
    validate_confidence_score(test_data['confidence_score_min'], response_dict['globalConfidenceScore'])

def validate_lid_response(test_data, response):
    response_dict = response['body']
    validate_language(test_data['language'], response_dict['requestedLanguages'])
    validate_detected_languages(test_data['detected_languages'], response_dict['detectedLanguages'])
    validate_lid_enabled(test_data['expected_lid_enabled'], response_dict['lidEnabled'])

def validate_smtp_response(test_data, response):
    response_dict = response['body']
    headers:dict = response['headers']

    validate_smtp_response_content_type(headers['Content-Type'])
    validate_smtp_response_mime_version(headers['MIME-Version'])
    validate_smtp_response_content_transfer_encoding(headers['Content-Transfer-Encoding'])

    validate_email_from(test_data['expected_email_from'], headers['From'])
    validate_email_to(test_data['sender_email'], headers['To'])

    validate_email_subject(test_data['expected_email_subject'], headers['Subject'])
    validate_email_reference(test_data['expected_email_reference'], headers['X-Reference'])

    validate_language(test_data['language'], response_dict['requestedLanguages'])
    validate_response_status(test_data, response)
    do_validate_recognition_status(test_data['recognition_status'], response_dict['recognitionStatus'])
    validate_rtf(test_data['rtf_max'], headers.get('X-RTF'))
    validate_confidence_score(test_data['confidence_score_min'], response_dict['globalConfidenceScore'])


def validate_smtp_response_content_type(actual_content_type):
    expected_content_type = get_config_value("smtptest", "email_response_header_content_type")
    validate(expected_content_type, actual_content_type, 'validate content type')

def validate_smtp_response_mime_version(actual_mime_version):
    expected_mime_version = get_config_value("smtptest", "email_response_header_mime_version")
    validate(expected_mime_version, actual_mime_version, 'validate mime version')

def validate_smtp_response_content_transfer_encoding(actual_content_transfer_encoding):
    expected_content_transfer_encoding = get_config_value("smtptest", "email_response_header_content_transfer_encoding")
    validate(expected_content_transfer_encoding, actual_content_transfer_encoding, 'validate content transfer_encoding')

def validate_email_from(expected_email_from, actual_email_from):
    validate(expected_email_from, actual_email_from, 'validate email from')

def validate_email_to(expected_email_to, actual_email_to):
    validate(expected_email_to, actual_email_to, 'validate email to')

def validate_email_subject(expected_email_subject, actual_email_subject):
    validate(expected_email_subject, actual_email_subject, 'validate email subject')

def validate_email_reference(expected_email_reference, actual_email_reference):
    validate(expected_email_reference, actual_email_reference, 'validate email reference')

def validate(expected, actual, message, contains=False, expected2=None):
    try:
        if contains and expected2 is None:
            assert expected in actual, f"Assertion Failed: '{expected}' not found in '{actual}'"
            reporter.report(message,f"Expected - {expected} contains Actual - {actual}")
        elif contains and expected2 is not None:
            assert expected in actual or expected2 in actual, f"Assertion Failed: '{expected}' or '{expected2}' not found in '{actual}'"
            reporter.report(message, f"Expected - {expected} || {expected2} contains Actual - {actual}")
        else:
            assert expected == actual, f"Assertion Failed: '{expected}' != '{actual}'"
            reporter.report(message, f"Expected - {expected} == Actual - {actual}")
    except AssertionError as ex:
        reporter.report(message, f"Expected - {expected} != Actual - {actual}")
        raise AssertionError(f"Expected ({expected}) != Actual ({actual})"
                             f"\nTraceback : {str(traceback.format_exception(etype=type(ex), value=ex, tb=ex.__traceback__))}")


import operator
def get_truth(input,op,compare):
    return op(input,compare)


def validate_numeric(expected,op,actual,message):
    rel_ops = {
        '>': operator.gt,
        '<': operator.lt,
        '>=': operator.ge,
        '<=': operator.le,
        '==': operator.eq,
        '!=': operator.ne
    }
    try:
        assert rel_ops[op](expected, actual) == True
        reporter.report(message,f"Expected - {expected} {op} Actual - {actual}")

    except AssertionError as ex:
        reporter.report(message,f"Assertion Failed: Expected - {expected} {op} Actual - {actual}")
        raise AssertionError(f"Assertion Failed: Expected - {expected} {op} Actual - {actual}",
                             f"\nTraceback : {str(traceback.format_exception(etype=type(ex), value=ex, tb=ex.__traceback__))}")

def validate_original_audio_in_response(test_data, response):
    audio_file_name = test_data['audio_file']
    audio_path = os.path.join(get_config_value('common', 'audio_files_repo'), audio_file_name)
    audio_string_from_file = str(read_from_file(audio_path), 'ascii').replace('\n', '').replace('\r', '')
    audio_string_from_response = response['body'].get('audio').replace('\n', '').replace('\r', '')
    assert audio_string_from_file == audio_string_from_response

def validate_speech_key_endpoint_in_logs(test_data, logs_output):
    pattern = re.compile(r'.*Using speech resource.*', re.MULTILINE)
    matches = pattern.findall(logs_output)
    result = re.search('.*Using speech resource: Key: (.*), Endpoint: (.*)$', ''.join(matches))
    speech_key_from_log = result.group(1)
    endpoint_from_log = result.group(2)
    assert test_data['speech_key'] == speech_key_from_log
    reporter.report('validate speech key', f"Expected - {test_data['speech_key']} is used")
    assert test_data['speech_endpoint'] == endpoint_from_log
    reporter.report('validate speech endpoint', f"Expected - {test_data['speech_endpoint']} is used")

def validate_after_deposit_ack_smtp_request(after_deposit_ack_response):
    email_subject = after_deposit_ack_response['headers']['Subject']
    validate_email_subject('Delivery Notification (Success)', email_subject)
    email_text = after_deposit_ack_response['body']['X-After_deposit_ack_message']
    assert 'Your message was successfully delivered to' in email_text