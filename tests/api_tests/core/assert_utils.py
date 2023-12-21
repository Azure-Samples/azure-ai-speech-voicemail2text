#!/usr/bin/env python
# coding: utf-8
# Copyright (c) Microsoft. All rights reserved.
# Licensed under the MIT license. See LICENSE.md file in the project root for full license information.

import traceback
from api_tests.core.reporter import reporter
from api_tests.core.constants.http_status_code import HttpStatusCode

def validate_request_ack_status_status_accepted(actual_status_code):
    expected_status_code=HttpStatusCode.ACCEPTED.value
    validate(actual_status_code, expected_status_code, 'validate request ack status code')

def validate_scrid(expected_scrid, actual_scrid):
    validate(expected_scrid, actual_scrid, 'validate response scrid')

def validate_response_status(expected_response_status, actual_response_status):
    validate(expected_response_status, actual_response_status, 'validate response status')

def validate_recognition_status(expected_recognition_status, actual_recognition_status):
    validate(expected_recognition_status, actual_recognition_status, 'validate recognition status')

def validate_external_request_id(expected_external_request_id, actual_external_request_id):
    validate(expected_external_request_id, actual_external_request_id, 'validate external request ID')

def validate_rtf(rtf_max, actual_rtf):
    validate_numeric(rtf_max, '>', actual_rtf, 'validate rtf')

def validate_confidence_score(confidence_score_min, actual_confidence_score):
    validate_numeric(confidence_score_min, '<', actual_confidence_score, 'validate confidence score')

def validate_language(language, actual_language):
    validate(language, actual_language, 'validate response requested languages')

def validate_detected_languages(detected_language, actual_detected_language):
    validate(detected_language, actual_detected_language, 'validate response detected languages')

def validate_lid_enabled(lid_enabled, actual_lid_enabled):
    validate(lid_enabled, actual_lid_enabled, 'validate response lid enabled')

def validate_http_response(scrid, external_request_id, test_data, response):
    response_dict = response['body']
    headers:dict = response['headers']
    validate_scrid(scrid, response_dict['scrid'])
    validate_external_request_id(external_request_id, response_dict['externalRequestID'])
    validate_response_status(test_data['status'], response_dict['reasonStatus'])
    validate_recognition_status(test_data['recognition_status'], response_dict['recognitionStatus'])
    validate_rtf(test_data['rtf_max'], headers.get('X-RTF'))
    validate_confidence_score(test_data['confidence_score_min'], response_dict['globalConfidenceScore'])

def validate_lid_response(test_data, response):
    response_dict = response['body']
    validate_language(test_data['language'], response_dict['requestedLanguages'])
    validate_detected_languages(test_data['detected_languages'], response_dict['detectedLanguages'])
    validate_lid_enabled(test_data['expected_lid_enabled'], response_dict['lidEnabled'])

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