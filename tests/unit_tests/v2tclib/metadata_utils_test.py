#!/usr/bin/env python
# coding: utf-8
# Copyright (c) Microsoft. All rights reserved.
# Licensed under the MIT license. See LICENSE.md file in the project root for full license information.



import sys,os
sys.path.append(os.path.join(os.path.abspath(os.curdir)))
from v2ticlib import metadata_utils

#Test for VTA-893: AC1
def test_default_truncate_lenghty_transcriptions_enabled():
  assert metadata_utils.is_truncate_lenghty_transcriptions_enabled() == False

#Test for VTA-893: AC1
def test_default_max_transcription_length():
  assert metadata_utils.get_default_max_transcription_length() == 5000