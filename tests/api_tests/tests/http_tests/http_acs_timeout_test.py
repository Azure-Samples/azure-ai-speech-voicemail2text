#!/usr/bin/env python
# coding: utf-8
# Copyright (c) Microsoft. All rights reserved.
# Licensed under the MIT license. See LICENSE.md file in the project root for full license information.


import pytest
from api_tests.tests.fixtures.http_server_fixture import http_server_fixture
from api_tests.tests.fixtures.http_listener_fixtures import http_listener_fixture
import api_tests.tests.http_tests.http_common_test as http_common_test
from api_tests.core.reporter import reporter
from api_tests.core.env_utils import set_os_env, unset_os_env
from api_tests.core.assert_utils import validate_recognition_status,validate_response_status


@pytest.fixture(scope="module", autouse=True)
def set_env_acs_client_audio_multiplier(request):
    setup_local_server =  request.config.getoption("--setup_local_server")
    if setup_local_server.lower() == "true":
        reporter.report("===set_env_acs_client_audio_multiplier -> Setting up os.environ() for acs_client->audio_multiplier fixture====")
        set_os_env('acs_client_audio_multiplier', '0.000001')

        yield

        reporter.report("===set_env_acs_client_audio_multiplier -> Tearing down os.environ() for http acs_client->audio_multiplier fixture====")
        unset_os_env('acs_client_audio_multiplier')



@pytest.mark.usefixtures('http_listener_fixture')
@pytest.mark.usefixtures('set_env_acs_client_audio_multiplier')
@pytest.mark.usefixtures('http_server_fixture')
@pytest.mark.httpacstimeout
@pytest.mark.httpregression
def test_acs_timeout(http_acs_timeout_test):
    test_data = http_acs_timeout_test
    response = http_common_test.test_http(test_data)
    validate_response_status(test_data, response)
    validate_recognition_status(test_data, response)