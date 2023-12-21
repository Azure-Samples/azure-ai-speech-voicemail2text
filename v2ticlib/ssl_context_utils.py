#!/usr/bin/env python
# coding: utf-8
# Copyright (c) Microsoft. All rights reserved.
# Licensed under the MIT license. See LICENSE.md file in the project root for full license information.



import ssl
import v2ticlib.constants.constants as CONSTANTS
import v2ticlib.config_utils as config_utils

verify_modes = {
  CONSTANTS.REQUIRED: ssl.CERT_REQUIRED, 
  CONSTANTS.OPTIONAL: ssl.CERT_OPTIONAL, 
  CONSTANTS.NONE: ssl.CERT_NONE
}

def create_server_ssl_context() -> ssl.SSLContext:
  verify_mode:ssl.VerifyMode = verify_modes.get(config_utils.get_verify_mode())
  cert_file = config_utils.get_cert_file()
  key_file = config_utils.get_key_file()
  certs_location_path = config_utils.get_authorized_client_certs_path()
  ssl_context = create_ssl_context(ssl.PROTOCOL_TLS_SERVER, verify_mode, cert_file, key_file, certs_location_path)
  return ssl_context

def create_client_ssl_context() -> ssl.SSLContext:
  cert_file = config_utils.get_client_cert_file()
  key_file = config_utils.get_client_key_file()
  certs_location_path = config_utils.get_client_trusted_certs_path()
  ssl_context = create_ssl_context(ssl.PROTOCOL_TLS_CLIENT, ssl.CERT_REQUIRED, cert_file, key_file, certs_location_path)
  return ssl_context

def create_ssl_context(protocol:int, verify_mode:ssl.VerifyMode, cert_file:str, key_file:str, certs_location_path:str) -> ssl.SSLContext:
  ssl_context = ssl.SSLContext(protocol=protocol)
  ssl_context.verify_mode = verify_mode
  ssl_context.minimum_version = ssl.TLSVersion.TLSv1_2
  ssl_context.load_cert_chain(certfile=cert_file, keyfile=key_file)
  ssl_context.load_verify_locations(capath=certs_location_path)
  return ssl_context