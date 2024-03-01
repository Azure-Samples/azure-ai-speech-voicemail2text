#!/usr/bin/env python
# coding: utf-8
# Copyright (c) Microsoft. All rights reserved.
# Licensed under the MIT license. See LICENSE.md file in the project root for full license information.



import sys,os
sys.path.append(os.path.join(os.path.abspath(os.curdir)))
from v2ticlib import metadata_utils
from tests.unit_tests.v2tclib.request_creator import RequestCreator
from Common.response_creator import ResponseCreator
from v2ticlib import request_utils
import v2ticlib.constants.fields as Fields
from unittest.mock import patch, MagicMock

request_creator = RequestCreator()
response_creator = ResponseCreator()
audio_bytes = b'test_audio_bytes'

#Test case for VTA-823 AC1
def test_default_log_transcriptions_enabled_value_false():
  assert metadata_utils.is_log_transcriptions_enabled() == False

#Test case for VTA-823 AC4
def test_log_transcriptions_enabled_from_request():
  request = request_creator.add_log_transcriptions_enabled(log_transcriptions_enabled='True')
  log_transcriptions_enabled_from_request = request_utils.is_log_transcriptions_enabled(request=request)
  assert log_transcriptions_enabled_from_request == True

#Test case for VTA-823 AC2
def test_log_transcriptions_enabled_false():
  test_recognition_result = {'text':'This is test for transcription enabled false',
                        'itn_text': 'This is test for transcription enabled false',
                        'display_text': 'This is test for transcription enabled false'}
  updated_recognition_result = response_creator.update_recognition_result_for_logging(recognition_result=test_recognition_result, fields=[Fields.TEXT, Fields.ITN_TEXT, Fields.DISPLAY_TEXT], logging_enabled=False)
  updated_text = updated_recognition_result[Fields.TEXT]
  updated_itn_text = updated_recognition_result[Fields.ITN_TEXT]
  updated_display_text = updated_recognition_result[Fields.DISPLAY_TEXT]

  assert 'not logging private content' in updated_text
  assert 'not logging private content' in updated_itn_text
  assert 'not logging private content' in updated_display_text

#Test case for VTA-823 AC3
def test_log_transcriptions_enabled_true():
  test_recognition_result = {'text':'This is test for transcription enabled true',
                        'itn_text':'This is test for transcription enabled true',
                        'display_text':'This is test for transcription enabled true'}
  updated_recognition_result = response_creator.update_recognition_result_for_logging(recognition_result=test_recognition_result, fields=[Fields.TEXT, Fields.ITN_TEXT, Fields.DISPLAY_TEXT], logging_enabled=True)
  updated_text = updated_recognition_result[Fields.TEXT]
  updated_itn_text = updated_recognition_result[Fields.ITN_TEXT]
  updated_display_text = updated_recognition_result[Fields.DISPLAY_TEXT]

  assert 'This is test for transcription enabled true' in updated_text
  assert 'This is test for transcription enabled true' in updated_itn_text
  assert 'This is test for transcription enabled true' in updated_display_text

#Test case for VTA-893 AC3
def test_truncate_lengthy_transcription_enabled_true():
  mock_truncate_lengthy_transcription_enabled_true = MagicMock(return_value=True)
  mock_max_transcription_length = MagicMock(return_value=15)
  recognition_result = {
    'conversion_status': 'Transcribed',
    'text': 'This is a long line text exceeding 15 characters',
    'itn_text': 'This is a long line text exceeding 15 characters',
    'display_text': 'This is a long line text exceeding 15 characters'
  }

  assert len(recognition_result[Fields.TEXT]) > 15
  assert len(recognition_result[Fields.ITN_TEXT]) > 15
  assert len(recognition_result[Fields.DISPLAY_TEXT]) > 15

  with patch('v2ticlib.request_utils.is_truncate_lenghty_transcriptions_enabled', mock_truncate_lengthy_transcription_enabled_true), \
  patch('v2ticlib.request_utils.get_max_transcription_length', mock_max_transcription_length):
    response_creator.resolve_text_truncation({}, recognition_result)

  assert len(recognition_result[Fields.TEXT]) == 15
  assert len(recognition_result[Fields.ITN_TEXT]) == 15
  assert len(recognition_result[Fields.DISPLAY_TEXT]) == 15

#Test case for VTA-893 AC2
def test_truncate_lengthy_transcription_enabled_false():
  mock_truncate_lengthy_transcription_enabled_false = MagicMock(return_value=False)
  mock_max_transcription_length = MagicMock(return_value=15)
  recognition_result = {
    'conversion_status': 'Transcribed',
    'text': 'This is a long line text exceeding 15 characters',
    'itn_text': 'This is a long line text exceeding 15 characters',
    'display_text': 'This is a long line text exceeding 15 characters'
  }

  original_text_length = len(recognition_result[Fields.TEXT])
  original_itn_text_length = len(recognition_result[Fields.ITN_TEXT])
  original_display_text_length = len(recognition_result[Fields.DISPLAY_TEXT])

  with patch('v2ticlib.request_utils.is_truncate_lenghty_transcriptions_enabled', mock_truncate_lengthy_transcription_enabled_false), \
  patch('v2ticlib.request_utils.get_max_transcription_length', mock_max_transcription_length):
    response_creator.resolve_text_truncation({}, recognition_result)

  assert len(recognition_result[Fields.TEXT]) == original_text_length
  assert len(recognition_result[Fields.ITN_TEXT]) == original_itn_text_length
  assert len(recognition_result[Fields.DISPLAY_TEXT]) == original_display_text_length

#test case for VTA-919 AC1
def test_respond_with_audio_enabled_default_value_false():
  request = request_creator.create_request_object('en-US', '50', '200')
  default_respond_with_audio_enabled = request_utils.respond_with_audio_enabled(request)
  assert default_respond_with_audio_enabled == False

#test case for VTA-919 AC1
def test_runtime_property_respond_with_audio_enabled():
  request = request_creator.create_request_respond_with_audio_enabled('True')
  respond_with_audio_enabled = request_utils.respond_with_audio_enabled(request)
  assert respond_with_audio_enabled == True

#test case for VTA-919 AC2
@patch('v2ticlib.request_utils.get_original_audio')
def test_original_audio_absent_in_response(mock_get_original_audio):
  mock_get_original_audio.return_value = audio_bytes
  recognition_result = {}
  request = request_creator.create_request_respond_with_audio_enabled('False')
  response_creator.resolve_respond_with_audio_enabled(request, recognition_result)
  assert recognition_result.get(Fields.ORIGINAL_AUDIO) == None

#test case for VTA-919 AC3
@patch('v2ticlib.request_utils.get_original_audio')
def test_original_audio_present_in_response(mock_get_original_audio):
  mock_get_original_audio.return_value = audio_bytes
  recognition_result = {}
  request = request_creator.create_request_respond_with_audio_enabled('True')
  response_creator.resolve_respond_with_audio_enabled(request, recognition_result)
  assert recognition_result[Fields.ORIGINAL_AUDIO] == audio_bytes