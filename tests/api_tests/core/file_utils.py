#!/usr/bin/env python
# coding: utf-8
# Copyright (c) Microsoft. All rights reserved.
# Licensed under the MIT license. See LICENSE.md file in the project root for full license information.



from api_tests.core.config_utils import get_config_value
import csv
import os
from api_tests.core.reporter import reporter
import v2ticlib.audio_utils as audio_utils

def read_from_file(file_path) -> bytes:
    with open(file_path, 'rb') as file:
        return file.read()

def get_audio_text(audio_file_name):
    audio_path = os.path.join(get_config_value('common', 'audio_files_repo'), audio_file_name)
    audio_bytes = read_from_file(audio_path)
    if not audio_utils.is_base64_encoded(audio_bytes):
        audio_bytes = audio_utils.encode_audio_bytes(audio_bytes)
    return audio_bytes

def read_test_data(file_path):
    with open(file_path, newline='',encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        return list(reader)