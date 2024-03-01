#!/usr/bin/env python
# coding: utf-8
# Copyright (c) Microsoft. All rights reserved.
# Licensed under the MIT license. See LICENSE.md file in the project root for full license information.



import unittest
from unittest.mock import patch
import sys, os
sys.path.append(os.path.join(os.path.abspath(os.curdir)))
from AcsClient.region_utils import RegionUtils

class TestRegionUtils(unittest.TestCase):
    def setUp(self):
        self.region_utils = RegionUtils()

    def test_update_stats_and_remove_inflight_request_region_failover_disabled(self):
        with patch.object(self.region_utils, '_is_region_failover_enabled', return_value=False):
            request = {'scrid': '12345'}
            self.region_utils.update_stats_and_remove_inflight_request(request)
            # Assert that the function returns without performing any actions
            # when region failover is disabled
            # You can add more assertions if needed

    def test_update_stats_and_remove_inflight_request_ignored_scrid(self):
        with patch.object(self.region_utils, '_is_region_failover_enabled', return_value=True):
            request = {'scrid': '235687'}
            self.region_utils._ignore_scrid_set = {'235687'}
            with patch('AcsClient.region_utils.debug') as mock_debug:
                self.region_utils.update_stats_and_remove_inflight_request(request)
                # Assert that the function returns without performing any actions
                # when the scrid is in the ignored scrid list
                # You can add more assertions if needed
                mock_debug.assert_called_with('scrid: 235687 is in ignored scrid list. do not perform region failover')

    def test_update_stats_and_remove_inflight_request_conversion_status_not_timeout(self):
        with patch.object(self.region_utils, '_is_region_failover_enabled', return_value=True):
            request = {'scrid': '5698745'}
            with patch('AcsClient.region_utils.request_utils.is_conversion_status_timeout', return_value=False):
                with patch('AcsClient.region_utils.log') as mock_log:
                    self.region_utils.update_stats_and_remove_inflight_request(request)
                    # Assert that the function resets the failure counter to 0
                    # when the conversion status is not timeout
                    # You can add more assertions if needed
                    mock_log.assert_called_with('reset failure counter value to 0')

    def test_update_stats_and_remove_inflight_request_conversion_status_timeout(self):
        with patch.object(self.region_utils, '_is_region_failover_enabled', return_value=True):
            request = {'scrid': '54321'}
            self.region_utils.add_inflight_request(request)
            with patch('AcsClient.region_utils.request_utils.is_conversion_status_timeout', return_value=True):
                with patch('AcsClient.region_utils.log') as mock_log:
                    with patch.object(self.region_utils, 'do_handle_region_failover') as mock_handle_failover:
                        self.region_utils.update_stats_and_remove_inflight_request(request)
                        # Assert that the function increments the failure counter
                        # and calls the do_handle_region_failover method
                        # You can add more assertions if needed
                        mock_log.assert_called_with('failure counter value after increment: 1')
                        mock_handle_failover.assert_called_with('54321')

if __name__ == '__main__':
    unittest.main()