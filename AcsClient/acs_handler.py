#!/usr/bin/env python
# coding: utf-8
# Copyright (c) Microsoft. All rights reserved.
# Licensed under the MIT license. See LICENSE.md file in the project root for full license information.

from AcsClient.acs_client import AcsClient
from AcsClient.acs_client_lid_enabled import AcsClientLid
import v2ticlib.request_utils as request_utils
import v2ticlib.constants.fields as fields
from AcsClient.region_utils import RegionUtils

class AcsHandler():
    def __init__(self):
        self._region_utils = RegionUtils()
        self._acs_client = AcsClient()
        self._acs_client_lid = AcsClientLid()
        self._acs_client_handler = {}
        lid_enabled = True
        lid_disabled = False
        self._acs_client_handler[lid_disabled] = self._acs_client
        self._acs_client_handler[lid_enabled] = self._acs_client_lid

    async def transcribe(self, request):
        scrid = request[fields.SCRID]
        lid_enabled = request_utils.is_lid_enabled(request)
        acs_handler: AcsClient = self._acs_client_handler[lid_enabled]
        try:
            self._region_utils.add_inflight_request(request)
            await acs_handler.transcribe(request)
        finally:
            self._region_utils.update_stats_and_remove_inflight_request(request)