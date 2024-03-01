#!/usr/bin/env python
# coding: utf-8
# Copyright (c) Microsoft. All rights reserved.
# Licensed under the MIT license. See LICENSE.md file in the project root for full license information.

import yaml

def read_config_map(file_path):
    with open(file_path, 'r') as file:
        config_map_data = yaml.safe_load(file)
    return config_map_data

def get_value_from_config_map(config_map_data, key):
    # Assuming the ConfigMap structure follows the standard format with 'data' field
    data_field = config_map_data.get('data', {})
    return data_field.get(key, None)