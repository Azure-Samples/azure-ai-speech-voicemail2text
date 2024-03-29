#!/usr/bin/env python
# coding: utf-8
# Copyright (c) Microsoft. All rights reserved.
# Licensed under the MIT license. See LICENSE.md file in the project root for full license information.


import pytest
from api_tests.tests.fixtures.http_server_fixture import http_server_fixture
from api_tests.tests.fixtures.http_listener_fixtures import http_listener_fixture
import api_tests.tests.http_tests.http_common_test as http_common_test
from api_tests.core.assert_utils import validate_recognition_status, validate_lid_enabled


@pytest.mark.usefixtures('http_listener_fixture')
@pytest.mark.usefixtures('http_server_fixture')
@pytest.mark.fixt_data()
@pytest.mark.httpexceedlimit
@pytest.mark.httpregression
@pytest.mark.httppodregression
def test_audio_is_transcribed_using_lid_exceed_limit(http_lid_language_limit_exceed_test):
    test_data = http_lid_language_limit_exceed_test
    response = http_common_test.test_http(test_data)
    validate_lid_enabled(test_data['lid_enabled'], response['body']['lidEnabled'])
    validate_recognition_status(test_data, response)
