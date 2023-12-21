#!/usr/bin/env python
# coding: utf-8
# Copyright (c) Microsoft. All rights reserved.
# Licensed under the MIT license. See LICENSE.md file in the project root for full license information.



import pytest
import sys,os
from unittest.mock import patch
sys.path.append(os.path.join(os.path.abspath(os.curdir)))
from Common.Ejector.smtp_ejector import SmtpEjector
from response_creator import ResponseCreator

@pytest.mark.asyncio
async def test_for_smtp_timeout():
  smtp_ejector = SmtpEjector()
  response_creator = ResponseCreator()
  response = response_creator.create_smtp_response('','',{},{})
  with patch('v2ticlib.smtp_client_utils.send', side_effect=TimeoutError("Timout occured")):
    with pytest.raises(Exception) as ex:
      await smtp_ejector.eject({},response)
    assert ex.type == TimeoutError

@pytest.mark.asyncio
async def test_for_successful_smtp_ejection():
  smtp_ejector = SmtpEjector()
  response_creator = ResponseCreator()
  response = response_creator.create_smtp_response('','',{},{})
  with patch('v2ticlib.smtp_client_utils.send', return_value=250):
    response_code = await smtp_ejector.eject({}, response)
  assert response_code == 250