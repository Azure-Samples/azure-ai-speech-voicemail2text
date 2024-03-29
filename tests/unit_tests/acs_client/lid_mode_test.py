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
from AcsClient.acs_client_lid_enabled import AcsClientLid
import azure.cognitiveservices.speech as speechsdk

class TestLidModeUtils(unittest.TestCase):
    def test_lid_mode_value_AtStartHighAccuracy_injected_in_dictionary_at_runtime(self):
        request_creator = RequestCreator()
        request = request_creator.create_acs_client_with_field_value('True','AtStartHighAccuracy','Raw')
        language_configuration_utils.resolve(request)
        acs_client = request[Fields.METADATA][Fields.ACS_CLIENT]
        assert acs_client[Fields.LID_MODE] == 'AtStartHighAccuracy'

    def test_lid_mode_value_Continuous_injected_in_dictionary_at_runtime(self):
        request_creator = RequestCreator()
        request = request_creator.create_acs_client_with_field_value('True','Continuous','Masked')
        language_configuration_utils.resolve(request)
        acs_client = request[Fields.METADATA][Fields.ACS_CLIENT]
        assert acs_client[Fields.LID_MODE] == 'Continuous'

    def test_lid_mode_value_AtStart_injected_in_dictionary_at_runtime(self):
        request_creator = RequestCreator()
        request = request_creator.create_acs_client_with_field_value('True','AtStart','Removed')
        language_configuration_utils.resolve(request)
        acs_client = request[Fields.METADATA][Fields.ACS_CLIENT]    
        assert acs_client[Fields.LID_MODE] == 'AtStart'
    
    def test_acs_lid_mode_get_property_value_if_request_contain_lid_mode_value_as_blank(self):
        request_creator = RequestCreator()
        request = request_creator.create_acs_client_without_lid_mode()
        acs_client_lid_mode = AcsClientLid()
        lid_mode_property_value = acs_client_lid_mode.get_lid_mode(request)
        assert lid_mode_property_value in ['Continuous','AtStart','AtStartHighAccuracy']

    def test_lid_mode_with_speech_config_result(self):
        lid_modes = ["Continuous", "AtStart", "AtStartHighAccuracy"]
        for lid_mode in lid_modes:
            request_creator = RequestCreator()
            acs_client_lid_mode = AcsClientLid()
            request = request_creator.create_acs_client_with_field_value('True',lid_mode,'Raw')
            speech_config = acs_client_lid_mode.get_speech_config(request)
            print(speech_config.get_property(speechsdk.PropertyId.SpeechServiceConnection_LanguageIdMode))
            assert speech_config.get_property(speechsdk.PropertyId.SpeechServiceConnection_LanguageIdMode) == lid_mode

if __name__ == '__main__':
    unittest.main()