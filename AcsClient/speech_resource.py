#!/usr/bin/env python
# coding: utf-8
# Copyright (c) Microsoft. All rights reserved.
# Licensed under the MIT license. See LICENSE.md file in the project root for full license information.


class SpeechResource:
    def __init__(self, key, endpoint):
        self._key = key
        self._endpoint = endpoint

    @property
    def key(self):
        return self._key

    @property
    def endpoint(self):
        return self._endpoint
    
    def __str__(self):
        return f'Key: {self.get_masked_speech_key(self._key)}, Endpoint: {self._endpoint}'

    def get_masked_speech_key(self, speech_key):
        speech_key_length = len(speech_key)
        masked_speech_key = "*" * (speech_key_length-2)
        masked_speech_key += speech_key[-2:]
        return masked_speech_key