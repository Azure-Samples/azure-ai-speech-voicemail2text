#!/usr/bin/env python
# coding: utf-8
# Copyright (c) Microsoft. All rights reserved.
# Licensed under the MIT license. See LICENSE.md file in the project root for full license information.

import unittest
import pytest
import sys, os
sys.path.append(os.path.join(os.path.abspath(os.curdir)))
import v2ticlib.constants.fields as Fields
import v2ticlib.language_configuration_utils as language_configuration_utils
from tests.unit_tests.v2tclib.request_creator import RequestCreator
from unittest import mock
import AcsClient.constants.fields as Acs_Fields
from AcsClient.acs_client import AcsClient
from azure.cognitiveservices.speech.enums import ProfanityOption

class TestProfanityOption(unittest.TestCase):
    def test_profinity_option_value_Raw_injected_in_dictionary_at_runtime(self):
        request_creator = RequestCreator()
        request = request_creator.create_acs_client_with_field_value('True','AtStartHighAccuracy','Raw')
        language_configuration_utils.resolve(request)
        acs_client = request[Fields.METADATA][Fields.ACS_CLIENT]
        assert acs_client[Acs_Fields.PROFANITY_OPTION] == 'Raw'

    def test_profinity_option_value_Masked_injected_in_dictionary_at_runtime(self):
        request_creator = RequestCreator()
        request = request_creator.create_acs_client_with_field_value('True','AtStartHighAccuracy','Masked')
        language_configuration_utils.resolve(request)
        acs_client = request[Fields.METADATA][Fields.ACS_CLIENT]
        assert acs_client[Acs_Fields.PROFANITY_OPTION] == 'Masked'

    def test_profinity_option_value_Removed_injected_in_dictionary_at_runtime(self):
        request_creator = RequestCreator()
        request = request_creator.create_acs_client_with_field_value('True','AtStartHighAccuracy','Removed')
        language_configuration_utils.resolve(request)
        acs_client = request[Fields.METADATA][Fields.ACS_CLIENT]
        assert acs_client[Acs_Fields.PROFANITY_OPTION] == 'Removed'

    def test_profinity_option_absent_in_dictionary_at_runtime_it_throws_error(self):
        try:
            request_creator = RequestCreator()
            request = request_creator.create_acs_client_without_profinity_option()
            language_configuration_utils.resolve(request)
        except Exception as e:
            print(f"An error occurred: {e.__class__}")
            assert str(e.__class__) == "<class 'ValueError'>", f"Expected a ValueError, but got {e.__class__}"

    def test_profanity_option_get_value_from_request_as_Masked(self):
        request_creator = RequestCreator()
        acs_client = AcsClient()
        request = request_creator.create_acs_client_with_field_value('True','AtStartHighAccuracy','Masked')
        profanity_option_property_value = acs_client.get_profanity_option(request)
        print(profanity_option_property_value)
        assert profanity_option_property_value.name == 'Masked'

    def test_profanity_option_get_value_from_request_as_Removed(self):
        request_creator = RequestCreator()
        acs_client = AcsClient()
        request = request_creator.create_acs_client_with_field_value('True','AtStartHighAccuracy','Removed')
        profanity_option_property_value = acs_client.get_profanity_option(request)
        print(profanity_option_property_value)
        assert profanity_option_property_value.name == 'Removed'

    def test_profanity_option_get_value_from_request_as_Raw(self):
        request_creator = RequestCreator()
        acs_client = AcsClient()
        request = request_creator.create_acs_client_with_field_value('True','AtStartHighAccuracy','Raw')
        profanity_option_property_value = acs_client.get_profanity_option(request)
        print(profanity_option_property_value)
        assert profanity_option_property_value.name == 'Raw'

    def test_profanity_option_with_speech_config_result(self):
        profanity_options = ["Masked", "Removed", "Raw"]
        for profanity_option in profanity_options:
            request_creator = RequestCreator()
            request = request_creator.create_acs_client_with_field_value('True','AtStartHighAccuracy',profanity_option)
            acs_client = AcsClient()
            speech_config_details = acs_client.get_speech_config_details(request)
            speech_config = acs_client.get_speech_config(request)
            assert speech_config_details[Acs_Fields.PROFANITY_OPTION] == ProfanityOption[profanity_option]
            assert speech_config is not None, "speech_config should not be None"

if __name__ == '__main__':
    unittest.main()