#!/usr/bin/env python
# coding: utf-8
# Copyright (c) Microsoft. All rights reserved.
# Licensed under the MIT license. See LICENSE.md file in the project root for full license information.



import pytest
import sys,os
from unittest.mock import patch
sys.path.append(os.path.join(os.path.abspath(os.curdir)))
from v2ticlib import config_utils
from v2ticlib.constants import constants
from Common.Ejector.http_ejector import HttpEjector
from response_creator import ResponseCreator

def test_default_timeout():
  assert config_utils.get_timelength_property_secs(constants.EJECTOR, constants.TIMEOUT) == 30.0

@pytest.mark.asyncio
async def test_for_http_timeout():
  http_ejector = HttpEjector()
  response_creator = ResponseCreator()
  response = response_creator.create_http_response('',{},{})
  with patch('v2ticlib.http_client_utils.post', side_effect=TimeoutError("Timout occured")):
    with pytest.raises(Exception) as ex:
      await http_ejector.eject({},response)
    assert ex.type == TimeoutError

@pytest.mark.asyncio
async def test_successful_http_ejection():
  http_ejector = HttpEjector()
  response_creator = ResponseCreator()
  response = response_creator.create_http_response('',{},{})
  with patch('v2ticlib.http_client_utils.post', return_value=200):
    response_code = await http_ejector.eject({}, response)
  assert response_code == 200