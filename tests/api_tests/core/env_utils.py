#!/usr/bin/env python
# coding: utf-8
# Copyright (c) Microsoft. All rights reserved.
# Licensed under the MIT license. See LICENSE.md file in the project root for full license information.

import sys, os

def set_os_env(env_key, env_value):
    os.environ[env_key] = env_value

def unset_os_env(env_key):
    del os.environ[env_key]