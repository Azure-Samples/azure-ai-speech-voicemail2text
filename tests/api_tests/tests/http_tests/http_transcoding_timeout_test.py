#!/usr/bin/env python
# coding: utf-8
# Copyright (c) Microsoft. All rights reserved.
# Licensed under the MIT license. See LICENSE.md file in the project root for full license information.


import pytest
import os
from api_tests.tests.fixtures.http_server_fixture import http_server_fixture
from api_tests.tests.fixtures.http_listener_fixtures import http_listener_fixture
import api_tests.tests.http_tests.http_common_test as http_common_test
from api_tests.core.assert_utils import validate_notes
from api_tests.core.reporter import reporter
from api_tests.core.env_utils import set_os_env, unset_os_env


@pytest.fixture(scope="module", autouse=True)
def set_env_transcoding_timeout_fixture(request):
  reporter.report("===set_env_transcoding_timeout_fixture -> Setting up os.environ() for transcoder->terminate_after and transcoder-> kill_after fixture====")
  set_os_env('transcoder_terminate_after', '0 seconds')
  set_os_env('transcoder_kill_after', '0 seconds')

  yield

  reporter.report("===set_env_transcoding_timeout_fixture -> tearing down os.environ() for transcoder->terminate_after and transcoder-> kill_after fixture====")
  unset_os_env('transcoder_terminate_after')
  unset_os_env('transcoder_kill_after')



@pytest.mark.usefixtures('http_listener_fixture')
@pytest.mark.usefixtures('http_server_fixture')
@pytest.mark.usefixtures('set_env_transcoding_timeout_fixture')
@pytest.mark.httptranscodingtimeout
@pytest.mark.httpregression
def test_transcoding_timeout(http_transcoding_timeout_test):
    test_data = http_transcoding_timeout_test
    response = http_common_test.test_http(test_data)
    if os.name != "nt":
        http_common_test.valiate_success_external_request_id(response)
        validate_notes(test_data, response)
