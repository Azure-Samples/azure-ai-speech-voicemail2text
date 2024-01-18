#!/usr/bin/env python
# coding: utf-8
# Copyright (c) Microsoft. All rights reserved.
# Licensed under the MIT license. See LICENSE.md file in the project root for full license information.


import pytest

from api_tests.tests.fixtures.http_listener_fixtures import http_listener_fixture
import api_tests.tests.http_tests.http_common_test as http_common_test

@pytest.mark.usefixtures('http_listener_fixture')
@pytest.mark.httpsanity
@pytest.mark.httpregression
def test_sanity(http_sanity_test_data_tc):
    test_data = http_sanity_test_data_tc
    http_common_test.test_http(test_data)