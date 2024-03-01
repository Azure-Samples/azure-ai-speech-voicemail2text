#!/usr/bin/env python
# coding: utf-8
# Copyright (c) Microsoft. All rights reserved.
# Licensed under the MIT license. See LICENSE.md file in the project root for full license information.



import pytest
import api_tests.tests.smtp_tests.smtp_common_test as smtp_common_test
from api_tests.tests.fixtures.smtp_listener_fixtures import smtp_listener_fixture
from api_tests.tests.fixtures.smtp_server_fixture import smtp_server_fixture
from api_tests.core.reporter import reporter
from api_tests.core.env_utils import set_os_env, unset_os_env

@pytest.fixture(scope="module", autouse=True)
def set_after_deposit_ack_profile(request):
    reporter.report("===set_after_deposit_ack_profile -> Setting up os.environ() for smtptest->smtp_test_profiles_folder_local fixture====")
    set_os_env('smtptest_smtp_test_profiles_folder_local', 'tests/api_tests/resources/profiles/test_smtp_after_deposit_ack')
    set_os_env('smtptest_smtp_test_profiles_profile_local', 'tests.api_tests.resources.profiles.test_smtp_after_deposit_ack.profile.TestSmtpProfile')
    yield
    reporter.report("===set_after_deposit_ack_profile -> tearing down os.environ() for smtptest->smtp_test_profiles_folder_local fixture====")
    unset_os_env('smtptest_smtp_test_profiles_folder_local')
    unset_os_env('smtptest_smtp_test_profiles_profile_local')

@pytest.mark.usefixtures('smtp_listener_fixture')
@pytest.mark.usefixtures('smtp_server_fixture')
@pytest.mark.usefixtures('set_after_deposit_ack_profile')
@pytest.mark.smtpafterdepositack
@pytest.mark.asyncio
@pytest.mark.smtpregression
async def test_after_deposit_ack(smtp_sanity_test):
    test_data = smtp_sanity_test
    response = await smtp_common_test.test_smtp(test_data,after_deposit_ack_validate=True)
    smtp_common_test.validate_success_smtp_response(test_data, response)
