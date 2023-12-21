#!/usr/bin/env python
# coding: utf-8
# Copyright (c) Microsoft. All rights reserved.
# Licensed under the MIT license. See LICENSE.md file in the project root for full license information.



import sys, os
sys.path.append(os.path.join(os.path.abspath(os.curdir)))
import v2ticlib.constants.fields as Fields
import AcsClient.constants.fields as Acs_Fields

class RequestCreator():
    def __init__(self):
        self.request = {}
        self.add_metadata(self.request)
        self.metadata = self.request[Fields.METADATA]

    def get(self):
        return self.request

    def add_metadata(self, request):
        request[Fields.METADATA] = {}
        return self

    def add_language(self, language):
        self.metadata[Fields.LANGUAGE] = language

    def create_language_configuration(self):
        self.metadata[Fields.LANGUAGE_CONFIGURATION] = {}

    def add_language_configuration_entry(self, language:str, entry:dict):
        language_configuration = self.metadata[Fields.LANGUAGE_CONFIGURATION]
        language_configuration[language] = entry

    def create_language_configuration_entry(self, min_confidence_percentage_str, max_audio_length_str):
        entry = {}
        entry[Fields.MIN_CONFIDENCE_PERCENTAGE] = min_confidence_percentage_str
        entry[Fields.MAX_AUDIO_LENGTH_SECS] = max_audio_length_str
        return entry

    def create_single_language_with_matching_entry(self, language, min_confidence_percentage_str, max_audio_length_str):
        entry = self.create_language_configuration_entry(min_confidence_percentage_str, max_audio_length_str)
        self.add_language(language)
        self.create_language_configuration()
        self.add_language_configuration_entry(language, entry)
        return self.get()
    
    def create_request_object(self, language, min_confidence_percentage_str, max_audio_length_str):
        entry = self.create_language_configuration_entry(min_confidence_percentage_str, max_audio_length_str)
        self.add_language(language)
        self.create_language_configuration()
        self.add_language_configuration_entry(language, entry)
        return self.get()
    
    def create_acs_client(self):
        self.metadata[Fields.ACS_CLIENT] = {}

    def create_acs_client_without_lid(self):
        self.create_acs_client()
        self.metadata[Fields.ACS_CLIENT][Fields.LID_MODE] = 'AtStartHighAccuracy'
        self.metadata[Fields.ACS_CLIENT][Acs_Fields.PROFANITY_OPTION] = 'Masked'
        return self.get()
    
    def create_acs_client_with_lid_true(self):
        return self.create_acs_client_with_field_value('True','AtStartHighAccuracy','Masked')
    
    def create_acs_client_with_lid_false(self):
        return self.create_acs_client_with_field_value('False','AtStartHighAccuracy','Masked')
    
    def create_acs_client_with_lid_blank(self):
        return self.create_acs_client_with_field_value('','AtStartHighAccuracy','Masked')
    
    def create_acs_client_with_field_value(self, lid_enabled, lid_mode, profinity_options):
        self.create_acs_client()
        self.metadata[Fields.ACS_CLIENT][Fields.LID_ENABLED] = lid_enabled
        self.metadata[Fields.ACS_CLIENT][Fields.LID_MODE] = lid_mode
        self.metadata[Fields.ACS_CLIENT][Acs_Fields.PROFANITY_OPTION] = profinity_options
        return self.get()
    
    def create_acs_client_without_profinity_option(self):
        self.create_acs_client()
        self.metadata[Fields.ACS_CLIENT][Fields.LID_ENABLED] = True
        self.metadata[Fields.ACS_CLIENT][Fields.LID_MODE] = 'AtStartHighAccuracy'
        return self.get()
    
    def create_acs_client_without_lid_mode(self):
        self.create_acs_client()
        self.metadata[Fields.ACS_CLIENT][Fields.LID_ENABLED] = True
        self.metadata[Fields.ACS_CLIENT][Acs_Fields.PROFANITY_OPTION] = 'Masked'
        return self.get()