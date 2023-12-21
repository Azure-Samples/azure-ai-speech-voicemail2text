#!/usr/bin/env python
# coding: utf-8
# Copyright (c) Microsoft. All rights reserved.
# Licensed under the MIT license. See LICENSE.md file in the project root for full license information.



import sys, os
sys.path.append(os.path.join(os.path.abspath(os.curdir)))
import v2ticlib.constants.fields as Fields

class ResponseCreator():
  def update_response(self, response:dict, response_field:str, value:any):
    response[response_field] = value

  def create_http_response(self, return_url:str, headers:dict, body:dict) -> dict:
    response = {}
    self.update_response(response, Fields.RETURN_URL, return_url)
    self.update_response(response, Fields.HEADERS, headers)
    self.update_response(response, Fields.BODY, body)
    return response
  
  def create_smtp_response(self, mail_from:str, rcpt_to:str, headers:dict, body:dict) -> dict:
    response = {}
    self.update_response(response, Fields.MAIL_FROM, mail_from)
    self.update_response(response, Fields.RCPT_TO, rcpt_to)
    self.update_response(response, Fields.HEADERS, headers)
    self.update_response(response, Fields.BODY, body)
    return response
