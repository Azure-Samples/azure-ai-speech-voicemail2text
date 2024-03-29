#!/usr/bin/env python
# coding: utf-8
# Copyright (c) Microsoft. All rights reserved.
# Licensed under the MIT license. See LICENSE.md file in the project root for full license information.



import pytest
from api_tests.app.system_utils.make_utils import MakeUtils

@pytest.mark.makecommandquickstart
def test_make_quick_start():
    make_utils = MakeUtils()
    make_utils.quick_start(deployment='https')
    make_utils.destroy_pod(deployment='https')
    make_utils.clean(deployment='https')