#!/usr/bin/env python
# coding: utf-8
# Copyright (c) Microsoft. All rights reserved.
# Licensed under the MIT license. See LICENSE.md file in the project root for full license information.



import v2ticlib.request_utils as request_utils
import v2ticlib.metadata_utils as metadata_utils
import v2ticlib.config_utils as config_utils
import v2ticlib.constants.fields as Fields
import v2ticlib.constants.constants as Constants

class RequestValidator():
    def validate(self, request:dict):
        self.validate_audio(request)
        self.validate_lid_fallback_language(request)

    def validate_audio(self, request:dict):
        if request_utils.does_not_have_audio(request):
            raise ValueError("Missing audio")

    def validate_lid_fallback_language(self, request:dict):
        if request_utils.is_lid_enabled(request) == False:
            return
        if config_utils.is_lid_fallback_enabled() == False:
            return
        languages:list = request_utils.get_requested_languages(request)
        default_lid_fallback_language = metadata_utils.get_default_lid_fallback_language()
        if default_lid_fallback_language not in languages:
            raise ValueError(f'Language {default_lid_fallback_language} is not in the LID candidate languages list {languages}')