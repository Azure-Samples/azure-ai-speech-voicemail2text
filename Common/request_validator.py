#!/usr/bin/env python
# coding: utf-8
# Copyright (c) Microsoft. All rights reserved.
# Licensed under the MIT license. See LICENSE.md file in the project root for full license information.



import v2ticlib.request_utils as request_utils

class RequestValidator():
    def validate(self, request:dict):
        if request_utils.does_not_have_audio(request):
            raise ValueError("Missing audio")
