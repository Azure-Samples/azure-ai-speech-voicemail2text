#!/usr/bin/env python
# coding: utf-8
# Copyright (c) Microsoft. All rights reserved.
# Licensed under the MIT license. See LICENSE.md file in the project root for full license information.



import requests
from api_tests.core.reporter import reporter
from api_tests.core.config_utils import get_config_value

class RestClient:
    def __init__(self, base_url):
        """
        :param url: Set request url
        :param body: Set request body
        """
        self.base_url = base_url
        self.client_cert_file = get_config_value("certs", "client_cert_file")
        self.client_key_file = get_config_value("certs", "client_key_file")
        self.server_cert_file = get_config_value("certs", "server_cert_file")

    def post(self, service_endpoint, headers, body):
        """
        :param headers:
        :param service_endpoint: post request service endpoint
        :param body: post request body
        :return: response
        """
        complete_url = self.base_url + service_endpoint

        reporter.report("***Request before sending POST request***")
        reporter.report("Request URL",complete_url)
        reporter.report("Request Header",headers)

        # to use self signed cert on windows, the server cert (certs.server_cert_file) needs to be added to the trusted root store
        response = requests.post(url=complete_url, headers=headers, data=body, cert=(self.client_cert_file, self.client_key_file), verify=False)#verify=self.server_certs)

        reporter.report("***Response after sending POST request***")
        reporter.report("Response Status Code",response.status_code)
        reporter.report("Response Header",response.headers)


        return response