#!/usr/bin/env python
# coding: utf-8
# Copyright (c) Microsoft. All rights reserved.
# Licensed under the MIT license. See LICENSE.md file in the project root for full license information.



import typing
from Common.request_validator import RequestValidator
from v2ticlib.template_utils import template_utils
import v2ticlib.language_configuration_utils as language_configuration_utils
import v2ticlib.request_utils as request_utils
import v2ticlib.audio_utils as audio_utils
import v2ticlib.header_utils as header_utils

class RequestInjestor():
    def __init__(self):
        self._request_validator = RequestValidator()

    def injest(self, initial_request_content:dict, headers:typing.Mapping[str, str], body:bytes):
        updated_headers = header_utils.update_headers_with_escaped_values(headers)
        request = template_utils.render_request(initial_request_content, updated_headers)
        language_configuration_utils.resolve(request)
        self.resolve_audio(request, body)
        self._request_validator.validate(request)
        return request

    def resolve_audio(self, request:dict, body:bytes):
        audio_bytes = audio_utils.get_audio_bytes(body)
        request_utils.set_audio(request, audio_bytes)
        if request_utils.respond_with_audio_enabled(request):
            audio_string = audio_utils.encode_audio_bytes(audio_bytes)
            request_utils.set_original_audio(request, audio_string)
