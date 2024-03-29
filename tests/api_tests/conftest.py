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
import tests.api_tests.app.pod_setup.setup_pod_server as pod_server
import threading
from api_tests.core.reporter import reporter
from api_tests.core.docker_utils import wait_till_docker_container_start,check_pod_server_status


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
test_cases.append("http_region_failover_test")

test_cases.append("smtp_sanity_test")
test_cases.append("smtp_languages_test")
test_cases.append("smtp_empty_audio_test")
test_cases.append("smtp_after_deposit_ack_test")

def pytest_generate_tests(metafunc):
    for test_case in test_cases:
        if test_case in metafunc.fixturenames:
            test_data = get_test_data(test_case)
            metafunc.parametrize(test_case, test_data)



@pytest.fixture(scope="session",autouse=False)
def http_pod_fixture(request):
    test_http_deployment_name = get_config_value('podsetup', 'http_test_deployment_name')
    setup_local_server =  request.config.getoption("--setup_local_server")
    docker_container_name = get_config_value('podsetup','docker_container_name')
    is_server_thread_used = False

    # Start pod http server if setup_local_server is false
    if setup_local_server.lower() == "false":
        # Modify httptest_server_port port to nodeport if setup_local_server is false
        os.environ['httptest_server_port'] = get_config_value('httptest', 'http_server_port_pod')

        docker_container_start_timeout = int(get_config_value('podsetup','docker_container_start_timeout'))
        host = get_config_value('httptest', 'server_url').split("//")[1]
        port = int(get_config_value('httptest', 'server_port'))

        if check_pod_server_status(host, port, 5):
            reporter.report("===http_server_fixture -> POD HTTP SERVER ALREADY RUNNING===")

        else:
            # Start pod http server if setup_local_server is false
            server_thread = threading.Thread(target=pod_server.start_pod_server_using_thread, args=(test_http_deployment_name,),daemon=True)
            server_thread.start()
            is_server_thread_used = True
            # Wait for pod http server to be ready
            wait_thread = threading.Thread(target=wait_till_docker_container_start, args=(docker_container_name, docker_container_start_timeout, host, port), daemon=True)
            wait_thread.start()
            wait_thread.join()


    yield

    # Stop pod http server if setup_local_server is false
    if setup_local_server.lower() == "false":
        os.unsetenv('httptest_server_port')
        pod_server.stop_pod_server(test_http_deployment_name)
        if is_server_thread_used:
            server_thread.join()
        pod_server.cleanup_pod_server()
        reporter.report("===http_server_fixture -> POD HTTP SERVER STOPPED===")


@pytest.fixture(scope="session",autouse=False)
def smtp_pod_fixture(request):
    test_smtp_deployment_name = get_config_value('podsetup', 'smtp_test_deployment_name')
    setup_local_server =  request.config.getoption("--setup_local_server")
    docker_container_name = get_config_value('podsetup','docker_container_name')
    is_server_thread_used = False

    # Start pod http server if setup_local_server is false
    if setup_local_server.lower() == "false":
        # Modify httptest_server_port port to nodeport if setup_local_server is false
        os.environ['smtptest_smtp_server_port'] = get_config_value('smtptest', 'smtp_server_port_pod')

        docker_container_start_timeout = int(get_config_value('podsetup','docker_container_start_timeout'))
        host = get_config_value('smtptest', 'smtp_server_url')
        port = int(get_config_value('smtptest', 'smtp_server_port'))

        if check_pod_server_status(host, port, 5):
            reporter.report("===http_server_fixture -> POD SMTP SERVER ALREADY RUNNING===")
        else:
            # Start pod http server if setup_local_server is false
            server_thread = threading.Thread(target=pod_server.start_pod_server_using_thread,args=(test_smtp_deployment_name,),daemon=True)
            server_thread.start()
            is_server_thread_used = True

            # Wait for pod http server to be ready
            wait_thread = threading.Thread(target=wait_till_docker_container_start, args=(docker_container_name, docker_container_start_timeout, host, port), daemon=True)
            wait_thread.start()
            wait_thread.join()


    yield

    # Stop pod http server if setup_local_server is false
    if setup_local_server.lower() == "false":
        os.unsetenv('smtptest_smtp_server_port')
        pod_server.stop_pod_server(test_smtp_deployment_name)
        if is_server_thread_used:
            server_thread.join()
        pod_server.cleanup_pod_server()
        reporter.report("===smtp_pod_fixture -> POD SMTP SERVER STOPPED===")