#!/usr/bin/env python
# coding: utf-8
# Copyright (c) Microsoft. All rights reserved.
# Licensed under the MIT license. See LICENSE.md file in the project root for full license information.



import os
import configparser
from configparser import ExtendedInterpolation
import ast
from timelength import TimeLength
import v2ticlib.constants.constants as Constants
import v2ticlib.constants.fields as Fields

def get_env_property(base:str, property:str):
    base = base.replace('.', '_')
    env_property = property.replace('.', '_')
    value = os.getenv('_'.join([base, env_property]))
    return value

def get_env_property_or_default(base:str, property:str, default:str):
    value = get_env_property(base, property)
    if value is None:
        return default
    return value

config = configparser.ConfigParser(interpolation=ExtendedInterpolation())
config_base = Constants.V2TIC
config_file_name = get_env_property_or_default(config_base, 'config_file_path', 'etc/config/config.properties')
config.read(config_file_name)

def get_property(base:str, property:str, literal_eval=False):
    value = get_env_property(base, property)
    if value is None:
        value = config.get(base, property)

    if literal_eval == False:
        return value

    return ast.literal_eval(value)

def get_timelength_property(base:str, property:str) -> TimeLength:
    value = get_property(base, property)
    return TimeLength(value)

def get_timelength_property_secs(base:str, property:str) -> int:
    timelength: TimeLength = get_timelength_property(base, property)
    return timelength.to_seconds()

def get_timelength_property_msecs(base:str, property:str) -> int:
    timelength: TimeLength = get_timelength_property(base, property)
    return timelength.to_milliseconds()

def has_property(base:str, property:str):
    return config.has_option(base, property)

def get_logging_level():
    return get_property(config_base, 'logging_level')

def get_host():
    return get_property(config_base, 'host')

def get_port():
    return get_property(config_base, 'port', literal_eval=True)

def get_cert_file():
    return get_property(config_base, 'cert_file')

def get_key_file():
    return get_property(config_base, 'key_file')

def get_consume_request_timeout():
    return get_timelength_property_secs(config_base, 'consume_request_timeout')

def get_coroutine_execution_default_timeout():
    return get_timelength_property_secs(config_base, 'coroutine_execution_default_timeout')

def get_verify_mode():
    return get_property(config_base, 'verify_mode')

def get_authorized_client_certs_path():
    return get_property(config_base, 'authorized_client_certs_path')

def get_client_cert_file():
    return get_property(config_base, 'client_cert_file')

def get_client_key_file():
    return get_property(config_base, 'client_key_file')

def get_client_trusted_certs_path():
    return get_property(config_base, 'client_trusted_certs_path')

def is_lid_fallback_enabled():
    return get_property(Fields.ACS_CLIENT, Fields.LID_TYPE, False) == Constants.LID_FALLBACK

def get_locking_default_timeout():
    return get_timelength_property_secs(config_base, 'locking_default_timeout')