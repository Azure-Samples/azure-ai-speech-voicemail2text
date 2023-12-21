#!/usr/bin/env python
# coding: utf-8
# Copyright (c) Microsoft. All rights reserved.
# Licensed under the MIT license. See LICENSE.md file in the project root for full license information.



from api_tests.core.config_utils import get_config_value
from api_tests.app.http_utils.http_listener_client import HTTPListenerClient
from api_tests.core.rest_client.rest_client import RestClient


class TranscribeRequestSender:
    def __init__(self):
        self.server_url = get_config_value('httptest', 'server_url')
        self.server_port = int(get_config_value('httptest', 'server_port'))
        self.listener_host = HTTPListenerClient.listener_host
        self.listener_port = HTTPListenerClient.listener_port
        self.base_url = f"{self.server_url}:{self.server_port}"

    def send_transcribe_request(self, audio_language, content_encoding, content_type, audio, lid_enabled = "False", lid_mode = "AtStartHighAccuracy"):
        """
            :param audio_language: request header X-Language
            :param content_encoding: request header Content-Encoding
            :param content_type: request header Content-Type
            :param audio: request body
            :return: response
            """

        listener_url = f"https://{self.listener_host}:{self.listener_port}"
        header = {
            "X-Return-URL": listener_url,
            "X-Caller": get_config_value('httptest', 'caller'),
            "X-Reference": get_config_value('httptest', 'caller_id'),
            "X-Language": audio_language,
            "Content-Encoding": content_encoding,
            "Content-Type": content_type,
            "X-LidEnabled" : lid_enabled
        }

        if lid_enabled == "True":
            header["X-LidMode"] = lid_mode

        rest_client = RestClient(base_url=self.base_url)
        response = rest_client.post(service_endpoint="/transcribe", headers=header, body=audio)

        return response
