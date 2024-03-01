#!/usr/bin/env python
# coding: utf-8
# Copyright (c) Microsoft. All rights reserved.
# Licensed under the MIT license. See LICENSE.md file in the project root for full license information.


import pytest
from api_tests.tests.fixtures.http_server_fixture import http_server_fixture
from api_tests.tests.fixtures.http_listener_fixtures import http_listener_fixture
import api_tests.tests.http_tests.http_common_test as http_common_test
from api_tests.core.assert_utils import validate_notes
from api_tests.core.reporter import reporter
from api_tests.core.env_utils import set_os_env, unset_os_env

@pytest.fixture(scope="module", autouse=True)
def set_env_config_file_path_fixture(request):
  reporter.report("===set_env_config_file_path_fixture -> Setting up os.environ() for v2tic->config_file_path fixture====")
  set_os_env('v2tic_config_file_path', 'tests/api_tests/resources/config/transcriber_test_config.properties')

  yield

  reporter.report("===set_env_config_file_path_fixture -> tearing down os.environ() for v2tic->config_file_path fixture====")
  unset_os_env('v2tic_config_file_path')

@pytest.mark.usefixtures('http_listener_fixture')
@pytest.mark.usefixtures('set_env_config_file_path_fixture')
@pytest.mark.usefixtures('http_server_fixture')
@pytest.mark.httptranscriptionfailure
@pytest.mark.httpregression
def test_transcription_failure(http_transcription_failure_test):
    test_data = http_transcription_failure_test
    response = http_common_test.test_http(test_data)
    http_common_test.valiate_success_external_request_id(response)
    validate_notes(test_data, response)