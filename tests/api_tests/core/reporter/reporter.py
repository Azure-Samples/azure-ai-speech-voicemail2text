#!/usr/bin/env python
# coding: utf-8
# Copyright (c) Microsoft. All rights reserved.
# Licensed under the MIT license. See LICENSE.md file in the project root for full license information.



def report(name,message=None):
    if message:
        print(f"{name} : {message}")
    else:
        print(name)