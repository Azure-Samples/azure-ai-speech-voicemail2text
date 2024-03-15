#!/usr/bin/env python
# coding: utf-8
# Copyright (c) Microsoft. All rights reserved.
# Licensed under the MIT license. See LICENSE.md file in the project root for full license information.


import pytest
import api_tests.tests.smtp_tests.smtp_common_test as smtp_common_test
from api_tests.tests.fixtures.smtp_listener_fixtures import smtp_listener_fixture
from api_tests.tests.fixtures.smtp_server_fixture import smtp_server_fixture


@pytest.mark.usefixtures('smtp_listener_fixture')
@pytest.mark.usefixtures('smtp_server_fixture')
@pytest.mark.usefixtures('smtp_pod_fixture')
@pytest.mark.smtplanguages
@pytest.mark.smtpregression
@pytest.mark.asyncio
@pytest.mark.smtppodregression
async def test_languages(smtp_languages_test):
    test_data = smtp_languages_test
    response = await smtp_common_test.test_smtp(test_data)
    smtp_common_test.validate_success_smtp_response(test_data, response)