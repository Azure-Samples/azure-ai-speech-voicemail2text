#!/usr/bin/env python
# coding: utf-8
# Copyright (c) Microsoft. All rights reserved.
# Licensed under the MIT license. See LICENSE.md file in the project root for full license information.


import pytest
import io
import re
from api_tests.tests.fixtures.http_server_fixture import http_server_fixture
from api_tests.tests.fixtures.http_listener_fixtures import http_listener_fixture
import api_tests.tests.http_tests.http_common_test as http_common_test
from api_tests.core.reporter import reporter
from api_tests.core.env_utils import set_os_env, unset_os_env
from api_tests.core.assert_utils import validate_recognition_status,validate_response_status,validate_speech_key_endpoint_in_logs
from contextlib import redirect_stdout
import tests.api_tests.core.config_utils as config_utils

@pytest.fixture(scope="module", autouse=True)
def set_env_acs_client_properties(request):
    setup_local_server =  request.config.getoption("--setup_local_server")
    speech_resources = config_utils.get_config_value('httptest', 'http_acs_speech_resources')
    if setup_local_server.lower() == "true":
        reporter.report("===set_env_acs_client_properties -> Setting up os.environ() for acs_client->audio_multiplier fixture====")
        set_os_env('acs_client_audio_multiplier', '0.000001')
        reporter.report("===set_env_acs_client_properties -> Setting up os.environ() for acs_client->speech_resources fixture====")
        set_os_env('acs_client_speech_resources', speech_resources)

        yield

        reporter.report("===set_env_acs_client_properties -> Tearing down os.environ() for http acs_client->audio_multiplier fixture====")
        unset_os_env('acs_client_audio_multiplier')
        reporter.report("===set_env_acs_client_properties -> Tearing down os.environ() for acs_client->speech_resources fixture====")
        unset_os_env('acs_client_speech_resources')



@pytest.mark.usefixtures('http_listener_fixture')
@pytest.mark.usefixtures('set_env_acs_client_properties')
@pytest.mark.usefixtures('http_server_fixture')
@pytest.mark.httpregionfailover
@pytest.mark.httpregression
def test_region_failover(http_region_failover_test):
    test_data = http_region_failover_test
    buffer = io.StringIO()
    with redirect_stdout(buffer):
        response = http_common_test.test_http(test_data)
    logs_output = buffer.getvalue()
    print(logs_output)
    validate_speech_key_endpoint_in_logs(test_data, logs_output)
    validate_response_status(test_data, response)
    validate_recognition_status(test_data, response)
    
