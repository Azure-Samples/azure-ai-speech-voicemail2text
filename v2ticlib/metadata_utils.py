#!/usr/bin/env python
# coding: utf-8
# Copyright (c) Microsoft. All rights reserved.
# Licensed under the MIT license. See LICENSE.md file in the project root for full license information.



import v2ticlib.constants.fields as Fields
import v2ticlib.config_utils as config_utils

supported_languages = set()

def get_property(property, literal_eval=False):
    return config_utils.get_property(Fields.METADATA, property, literal_eval=literal_eval)

def is_truncate_lenghty_transcriptions_enabled() -> bool:
    return get_property('truncate_lenghty_transcriptions_enabled', literal_eval=True)

def get_default_max_transcription_length() -> int:
    return get_property('default_max_transcription_length', literal_eval=True)

def is_log_transcriptions_enabled() -> bool:
    return get_property('log_transcriptions_enabled', literal_eval=True)

def get_default_language() -> str:
    return get_property('default_language', literal_eval=False)

def get_default_lid_languages() -> list:
    return get_property('default_lid_languages', literal_eval=True)

def get_default_thresholds() -> dict:
    return get_property('default_thresholds', literal_eval=True)

def get_default_lid_thresholds() -> dict:
    return get_property('default_lid_thresholds', literal_eval=True)

def get_supported_languages() -> set:
    global supported_languages
    if len(supported_languages) == 0:
        supported_languages = get_property('supported_languages', literal_eval=True)

    return supported_languages

def respond_with_audio_enabled() -> bool:
    return get_property('respond_with_audio_enabled', literal_eval=True)

def get_max_transcription_line_length() -> int:
    return get_property('max_transcription_line_length', literal_eval=True)

def get_default_lid_fallback_language() -> str:
    return get_property('default_lid_fallback_language', literal_eval=False)