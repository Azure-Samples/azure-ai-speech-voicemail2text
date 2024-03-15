#!/usr/bin/env python
# coding: utf-8
# Copyright (c) Microsoft. All rights reserved.
# Licensed under the MIT license. See LICENSE.md file in the project root for full license information.


import pytest

from api_tests.tests.fixtures.http_server_fixture import http_server_fixture
import api_tests.tests.http_tests.http_common_test as http_common_test
from api_tests.core.assert_utils import validate_request_ack_status_bad_request


@pytest.mark.usefixtures('http_server_fixture')
@pytest.mark.usefixtures('http_pod_fixture')
@pytest.mark.httpemptyaudio
@pytest.mark.httpregression
@pytest.mark.httppodregression
def test_empty_audio(http_empty_audio_test):
    test_data = http_empty_audio_test
    request_ack = http_common_test.send_request(test_data)
    validate_request_ack_status_bad_request(request_ack.status_code)