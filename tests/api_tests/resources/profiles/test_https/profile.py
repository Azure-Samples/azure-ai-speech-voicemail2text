#!/usr/bin/env python
# coding: utf-8
# Copyright (c) Microsoft. All rights reserved.
# Licensed under the MIT license. See LICENSE.md file in the project root for full license information.



import typing,sys,os
from Common.abstract_profile import AbstractProfile
import v2ticlib.constants.headers as Headers

class TestHttpsProfile(AbstractProfile):

    def get_mandatory_headers(cls):
        return [Headers.X_REFERENCE, Headers.X_RETURN_URL]

    def get_request_context(cls, context:dict[str, any], headers: typing.Mapping[str, str]) -> dict[str, any]:
        return context