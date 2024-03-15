#!/usr/bin/env python
# coding: utf-8
# Copyright (c) Microsoft. All rights reserved.
# Licensed under the MIT license. See LICENSE.md file in the project root for full license information.



import configparser
import os, ast

config = configparser.ConfigParser()
current_dir = os.path.dirname(os.path.abspath(__file__))
env_file_name = os.path.join(current_dir,'..','test_config.properties')

config.read(env_file_name)

def get_env_property(base:str, property:str):
    base = base.replace('.', '_')
    env_property = property.replace('.', '_')
    value = os.getenv('_'.join([base, env_property]))
    return value

def get_config_value(base, property):
    value = get_env_property(base, property)
    if value is None:
        value = config.get(base, property)
    return value

def get_local_server_timeout():
    return int(get_config_value('common', 'local_server_timeout'))