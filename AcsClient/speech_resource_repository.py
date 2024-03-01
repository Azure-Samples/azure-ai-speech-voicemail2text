#!/usr/bin/env python
# coding: utf-8
# Copyright (c) Microsoft. All rights reserved.
# Licensed under the MIT license. See LICENSE.md file in the project root for full license information.


from typing import Final
from v2ticlib.logger_utils import log
import v2ticlib.config_utils as config_utils
import AcsClient.constants.constants as Acs_Constants
from AcsClient.speech_resource import SpeechResource
from v2ticlib.lock_utils import get_lock_with_timeout as get_lock

class SpeechResourceRepository():

    def __init__(self):
        self._speech_resource_index = 0
        self._speech_resources = self._get_speech_resources()
        self._speech_resources_size = len(self._speech_resources)

    def _get_speech_resources(self):
        speech_resources = config_utils.get_property(Acs_Constants.ACS_CLIENT, "speech_resources", literal_eval=True)
        key_index = 0
        endpoint_index = 1
        return [SpeechResource(speech_resource[key_index], speech_resource[endpoint_index]) for speech_resource in speech_resources]

    def get_speech_resources_size(self):
        return self._speech_resources_size

    def get_speech_resource(self):
        with get_lock('region_failover_lock'):
            _speech_resource = self._speech_resources[self._speech_resource_index]
            return _speech_resource

    def switch_speech_resource(self):
        with get_lock('region_failover_lock'):
            self._speech_resource_index = (self._speech_resource_index + 1) % self._speech_resources_size
            log(f'switched to next speech resource index: {self._speech_resource_index}')

speech_resource_repository: Final[SpeechResourceRepository] = SpeechResourceRepository()