#!/usr/bin/env python
# coding: utf-8
# Copyright (c) Microsoft. All rights reserved.
# Licensed under the MIT license. See LICENSE.md file in the project root for full license information.



import pytest
import api_tests.tests.smtp_tests.smtp_common_test as smtp_common_test
from api_tests.tests.fixtures.smtp_server_fixture import smtp_server_fixture
from api_tests.core.assert_utils import validate_request_ack_status_status_bad_smtp_request


@pytest.mark.usefixtures('smtp_server_fixture')
@pytest.mark.usefixtures('smtp_pod_fixture')
@pytest.mark.smtpemptyaudio
@pytest.mark.asyncio
@pytest.mark.smtpregression
@pytest.mark.smtppodregression
async def test_smtp_empty_audio(smtp_empty_audio_test):
    test_data = smtp_empty_audio_test
    try:
        await smtp_common_test.send_request(test_data)
    except Exception as e:
        validate_request_ack_status_status_bad_smtp_request(str(e))
