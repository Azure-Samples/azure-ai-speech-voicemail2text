#!/usr/bin/env python
# coding: utf-8
# Copyright (c) Microsoft. All rights reserved.
# Licensed under the MIT license. See LICENSE.md file in the project root for full license information.



import configparser
import os

config = configparser.ConfigParser()
current_dir = os.path.dirname(os.path.abspath(__file__))
env_file_name = os.path.join(current_dir,'..','test_config.properties')

config.read(env_file_name)


def get_config_value(base, property):
    return config.get(base, property)
