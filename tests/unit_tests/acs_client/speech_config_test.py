#!/usr/bin/env python
# coding: utf-8
# Copyright (c) Microsoft. All rights reserved.
# Licensed under the MIT license. See LICENSE.md file in the project root for full license information.


import sys,os,io
import json
from jinja2 import Environment, FileSystemLoader
from contextlib import redirect_stdout
sys.path.append(os.path.join(os.path.abspath(os.curdir)))
from tests.unit_tests.v2tclib.request_creator import RequestCreator
from AcsClient.acs_client_lid_enabled import AcsClientLid
from AcsClient.acs_client import AcsClient
from v2ticlib.template_utils import TemplateUtils
import v2ticlib.constants.fields as Fields
from AcsClient.speech_resource_repository import speech_resource_repository

template_dir = "tests/unit_tests/etc/profiles/sample_https/templates"
template_name = "request.j2"

request_creator = RequestCreator()
template_utils = TemplateUtils()

def render_template(data=None):
        environment = Environment(loader=FileSystemLoader(template_dir))
        template = environment.get_template(template_name)
        output = template.render({"request": data})
        return json.loads(output)

def create_request_from_jinja_template(test_data:dict):
    data = {
      'acs_client': {
        'lid_enabled': test_data['lid_enabled'],
        'lid_mode': test_data['lid_mode'],
        'profanity_option': test_data['profanity_option'],
        'tagging_enabled':test_data['tagging_enabled'],
        'tag_value':test_data['tag_value']
      }
    }
    request = render_template(data)
    request[Fields.METADATA][Fields.SPEECH_RESOURCE] = speech_resource_repository.get_speech_resource()
    return request

#Test for VTA-822 AC1 & AC2
def test_runtime_properties_in_speech_config_with_lid_enabled_true():
  test_data = {"lid_enabled": "True", "lid_mode":"Continuous", "profanity_option": "Removed", "tagging_enabled":"True", "tag_value": "TestTag1"}
  request = create_request_from_jinja_template(test_data)
  acs_client = AcsClientLid()
  f = io.StringIO()
  with redirect_stdout(f):
    acs_client.log_speech_config_details(request)
  out = f.getvalue()
  assert 'Continuous' in out
  assert 'Removed' in out
  assert 'TestTag1' in out
  assert "'tagging_enabled': True" in out

#Test for VTA-822 AC1 & AC2
def test_runtime_properties_in_speech_config_with_lid_enabled_false():
    test_data = {"lid_enabled": "False", "lid_mode":"Continuous", "profanity_option": "Removed", "tagging_enabled":"True", "tag_value": "TestTag1"}
    request = create_request_from_jinja_template(test_data)
    acs_client = AcsClient()
    f = io.StringIO()
    with redirect_stdout(f):
      acs_client.log_speech_config_details(request)
    out = f.getvalue()
    assert 'Continuous' not in out
    assert 'Removed' in out
    assert 'TestTag1' in out
    assert "'tagging_enabled': True" in out

#Test for VTA-822 AC3
def test_non_runtime_properties_in_speech_config():
    test_data = {"lid_enabled": "False", "lid_mode":"Continuous", "profanity_option": "Removed", "tagging_enabled":"True", "tag_value": "TestTag1"}
    request = create_request_from_jinja_template(test_data)
    acs_client = AcsClient()
    f = io.StringIO()
    with redirect_stdout(f):
      acs_client.log_speech_config_details(request)
    out = f.getvalue()
    assert "'hard_tat_handler': True" in out
    assert "'word_level_confidence': 'False'" in out
    assert "'silence.segment_silence_timeout': '1000'" in out