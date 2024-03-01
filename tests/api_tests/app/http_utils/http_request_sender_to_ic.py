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

    def send_transcribe_request(self, headers, audio):
        """
        :param headers: request headers
        :param audio: request body
        :return: response
        """

        listener_url = f"https://{self.listener_host}:{self.listener_port}"
        headers['X-Return-URL'] = listener_url

        rest_client = RestClient(base_url=self.base_url)
        response = rest_client.post(service_endpoint="/transcribe", headers=headers, body=audio)

        return response
