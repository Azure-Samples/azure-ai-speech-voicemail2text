#!/usr/bin/env python
# coding: utf-8
# Copyright (c) Microsoft. All rights reserved.
# Licensed under the MIT license. See LICENSE.md file in the project root for full license information.



import pytest
import os
import datetime
import sys
sys.path.append(os.path.join(os.path.abspath(os.curdir)))
from api_tests.core.file_utils import read_test_data
from api_tests.core.config_utils import get_config_value


# Set the custom environment variable with the timestamp
timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
os.environ["TEST_TIMESTAMP"] = timestamp

@pytest.hookimpl(tryfirst=True)
def pytest_configure(config):
    if config.option.html_report:
        timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
        config.option.htmlpath = f"report_{timestamp}.html"

def pytest_html_results_summary(prefix, summary, postfix):
    timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
    report_file = f"reports/report_{timestamp}.html"
    summary.append(f"Report: {report_file}")

def pytest_configure(config):
    config.addinivalue_line(
        "markers", "print_assertion_details: Print assertion details in the HTML report"
    )

def pytest_html_results_table_row(report, cells):
    #if 'print_assertion_details' in report.keywords and report.failed:
    #    for entry in report.longrepr.reprcrash.message.split('\n'):
    #        cells.append(entry)
    pass


# Define a custom pytest option for the command-line argument
def pytest_addoption(parser):
    parser.addoption("--setup_local_server", action="store", default="True", help="Setup local server for testing")


def read_test_data_from_csv(test_type,test_data_file_name):
    test_data_repo = None
    current_dir = os.path.dirname(os.path.abspath(__file__))

    if test_type == "http":
        test_data_repo = get_config_value('httptest', 'http_test_data_repo')
    if test_type == "smtp":
        test_data_repo = get_config_value('smtptest', 'smtp_test_data_repo')

    test_data_csv = read_test_data(f"{current_dir}{test_data_repo}{test_data_file_name}")
    return test_data_csv

def get_test_data(test_case):
    protocol = test_case.split("_")[0]
    test_data_file_name = get_config_value(f'{protocol}test', f'{test_case}_data')
    test_data_csv = read_test_data_from_csv(protocol, test_data_file_name)
    return test_data_csv

test_cases = []
test_cases.append("http_sanity_test")
test_cases.append("http_languages_test")
test_cases.append("http_codecs_test")
test_cases.append("http_large_audio_test")
test_cases.append("http_lid_test")
test_cases.append("http_empty_audio_test")
test_cases.append("http_bad_audio_test")
test_cases.append("http_original_audio_in_response_test")
test_cases.append("http_acs_timeout_test")
test_cases.append("http_transcoding_timeout_test")
test_cases.append("http_transcription_failure_test")
test_cases.append("http_lid_language_limit_exceed_test")

test_cases.append("smtp_sanity_test")
test_cases.append("smtp_languages_test")
test_cases.append("smtp_empty_audio_test")
test_cases.append("smtp_after_deposit_ack_test")

def pytest_generate_tests(metafunc):
    for test_case in test_cases:
        if test_case in metafunc.fixturenames:
            test_data = get_test_data(test_case)
            metafunc.parametrize(test_case, test_data)
