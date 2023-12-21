#!/usr/bin/env python
# coding: utf-8
# Copyright (c) Microsoft. All rights reserved.
# Licensed under the MIT license. See LICENSE.md file in the project root for full license information.



def is_blank(string:str):
    return string is None or string.strip() == ""

def is_not_blank(string:str):
    return not is_blank(string)

def default_if_empty(string:str, default:str):
    if is_blank(string):
        return default
    return string

def is_valid_int(string:str) -> bool:
    is_valid:bool = False
    try:
        int(string)
        is_valid = True
    except ValueError:
        pass
    return is_valid

def is_invalid_int(string:str) -> bool:
    return not is_valid_int(string)