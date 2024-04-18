#!/usr/bin/env python
# coding: utf-8
# Copyright (c) Microsoft. All rights reserved.
# Licensed under the MIT license. See LICENSE.md file in the project root for full license information.


import v2ticlib.config_utils as config_utils
import v2ticlib.constants.constants as Constants

def get_enable_strict_mode():
    return config_utils.get_property(Constants.JSON, "enable_strict_mode", literal_eval=True)

def get_replace_characters_list():
    return config_utils.get_property(Constants.JSON, 'replace_characters_list', literal_eval=True)

def replace_characters(string_value):
    if not isinstance(string_value, str):
        return string_value
    for replace_char_tuple in get_replace_characters_list():
        key = replace_char_tuple[0]
        value = replace_char_tuple[1]
        if value in string_value:
            continue
        string_value = string_value.replace(key, value)
    return string_value

def update_json_values(obj):
    new_obj = {}
    if isinstance(obj, dict):
        for key in obj:
            new_obj[key] = update_json_values(obj[key])
    elif isinstance(obj, list):
        for i in range(len(obj)):
            new_obj[i] = update_json_values(obj[i])
    else:
        new_obj = replace_characters(obj)
    return new_obj