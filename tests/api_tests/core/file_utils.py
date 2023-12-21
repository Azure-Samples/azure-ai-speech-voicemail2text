#!/usr/bin/env python
# coding: utf-8
# Copyright (c) Microsoft. All rights reserved.
# Licensed under the MIT license. See LICENSE.md file in the project root for full license information.



from api_tests.core.config_utils import get_config_value
import csv
import os
import base64
import textwrap
from api_tests.core.reporter import reporter

def read_text_from_file(file_path):
    with open(file_path, 'rb') as file:
        audio_bytes = base64.decodebytes(file.read())
    return str(base64.encodebytes(audio_bytes), 'ascii')
def file_to_base64(file_path):
    with open(file_path, "rb") as file:
        return str(base64.encodebytes(file.read()), 'ascii')

def get_audio_text(audio_file_dir,audio_file_name):
    current_dir = os.path.dirname(os.path.abspath(__file__))
    test_data_dir = os.path.join(current_dir, '..')
    audio_path = test_data_dir + get_config_value('common', 'audio_files_repo') + audio_file_dir + audio_file_name
    file_type = audio_file_name.split(".")[-1]

    if file_type == "txt":
        audio_text = read_text_from_file(audio_path)
    else:
        audio_text = file_to_base64(audio_path)
    return audio_text


def read_test_data(file_path):
    with open(file_path, newline='',encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        return list(reader)


def break_long_lines(message, max_line_length=100):
    lines = message.split('\n')
    wrapped_lines = []

    for line in lines:
        if len(line) > max_line_length:
            wrapped_lines.extend(textwrap.wrap(line, width=max_line_length))
        else:
            wrapped_lines.append(line)

    return '\n'.join(wrapped_lines)
