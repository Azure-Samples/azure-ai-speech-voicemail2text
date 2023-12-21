#!/usr/bin/env python
# coding: utf-8
# Copyright (c) Microsoft. All rights reserved.
# Licensed under the MIT license. See LICENSE.md file in the project root for full license information.



from abc import ABC, abstractmethod
import v2ticlib.string_utils as string_utils
import v2ticlib.config_utils as config_utils
import v2ticlib.constants.constants as CONSTANTS

class Ejector(ABC):
    @abstractmethod
    async def eject(self, request, response) -> str:
        pass

    def get_timeout(self):
        return config_utils.get_timelength_property_secs(CONSTANTS.EJECTOR, CONSTANTS.TIMEOUT)