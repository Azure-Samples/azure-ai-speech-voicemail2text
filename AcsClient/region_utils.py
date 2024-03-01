#!/usr/bin/env python
# coding: utf-8
# Copyright (c) Microsoft. All rights reserved.
# Licensed under the MIT license. See LICENSE.md file in the project root for full license information.

import v2ticlib.config_utils as config_utils
from v2ticlib.logger_utils import log, debug
import AcsClient.constants.constants as Acs_Constants
import v2ticlib.constants.fields as Fields
import v2ticlib.request_utils as request_utils
from AcsClient.speech_resource_repository import speech_resource_repository
from v2ticlib.lock_utils import get_lock_with_timeout as get_lock

class RegionUtils():

  def __init__(self):
    self._failures = 0
    self._ignore_scrid_set = set()
    self._in_flight_scrids = []
    self._region_failover_threshold = self._get_region_failover_threshold()

  def _get_region_failover_threshold(self):
    return config_utils.get_property(Acs_Constants.ACS_CLIENT, "region_failover_threshold", literal_eval=True)

  def _get_region_failover_enabled(self):
    return config_utils.get_property(Acs_Constants.ACS_CLIENT, "region_failover_enabled", literal_eval=True)

  def _is_region_failover_enabled(self):
    return self._get_region_failover_enabled() and speech_resource_repository.get_speech_resources_size() > 1
  
  def add_inflight_request(self, request):
    with get_lock('region_failover_lock'):
      scrid = request[Fields.SCRID]
      self._in_flight_scrids.append(scrid)

  def update_stats_and_remove_inflight_request(self, request):
    with get_lock('region_failover_lock'):
      if not self._is_region_failover_enabled():
        debug('region failover is not enabled.')
        return

      scrid = request[Fields.SCRID]
      if scrid in self._ignore_scrid_set:
        debug(f'scrid: {scrid} is in ignored scrid list. do not perform region failover')
        self._ignore_scrid_set.remove(scrid)
        return

      if not request_utils.is_conversion_status_timeout(request):
        log('reset failure counter value to 0')
        self._failures = 0
        return

      self._failures += 1
      log(f'failure counter value after increment: {self._failures}')

      self.do_handle_region_failover(scrid)

      self.remove_inflight_request(request)

  def do_handle_region_failover(self, scrid):
    with get_lock('region_failover_lock'):
      counter_value = self._failures
      if counter_value >= self._region_failover_threshold:
        log('max threshold reached. switching to next speech key and endpoint')
        self._ignore_scrid_set.update(self._in_flight_scrids)
        speech_resource_repository.switch_speech_resource()
        log('reset failure counter value to 0')
        self._failures = 0

      if scrid in self._ignore_scrid_set:
        self._ignore_scrid_set.remove(scrid)

  def remove_inflight_request(self, request):
    try:
      with get_lock('region_failover_lock'):
        scrid = request[Fields.SCRID]
        self._in_flight_scrids.remove(scrid)
    except ValueError:
      log(f'Message with scrid: {scrid} is already processed')
