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
        self.cert_dir = get_config_value("certs", "certs_dir")
        #self.client_certificate = 'etc/certs/client/certificate.pem'#self.cert_dir + get_config_value("certs", "client_certificate")
        #self.client_private_key = 'etc/certs/client/private_key.pem'#self.cert_dir + get_config_value("certs", "client_private_key")
        #self.verify_server_certificate = 'etc/certs/certificate.pem'#self.cert_dir + get_config_value("certs", "verify_server_certificate")
        self.client_certificate = 'etc/certs/client/certificate.pem'#cert_dir + get_config_value("certs", "client_certificate")
        self.client_private_key = 'etc/certs/client/private_key.pem'#cert_dir + get_config_value("certs", "client_private_key")
        self.server_certs = 'etc/certs/certificate.pem'#cert_dir + get_config_value("certs", "listener_smtp_ca_certs")

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


        response = requests.post(url=complete_url, headers=headers, data=body, cert=(self.client_certificate, self.client_private_key), verify=False)#verify=self.server_certs)


        reporter.report("***Response after sending POST request***")
        reporter.report("Response Status Code",response.status_code)
        reporter.report("Response Header",response.headers)


        return response