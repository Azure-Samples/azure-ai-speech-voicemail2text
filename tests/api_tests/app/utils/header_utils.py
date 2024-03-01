#!/usr/bin/env python
# coding: utf-8
# Copyright (c) Microsoft. All rights reserved.
# Licensed under the MIT license. See LICENSE.md file in the project root for full license information.

import v2ticlib.constants.fields as Fields
import AcsClient.constants.fields as AcsFields

def get_or_default(test_data:dict, key:str, default_value:str) -> str:
    return test_data.get(key, default_value)

def create_headers(test_data:dict, extra_headers:dict) -> dict:
    headers = {
        "X-Language": test_data.get(Fields.LANGUAGE),
        "Content-Encoding": test_data.get('content_encoding'),
        "Content-Type": test_data.get('content_type'),
        "X-LogTranscriptionEnabled": get_or_default(test_data, Fields.LOG_TRANSCRIPTIONS_ENABLED, "False"),
        "X-RespondWithAudioEnabled": get_or_default(test_data, Fields.RESPOND_WITH_AUDIO_ENABLED, "False"),
        "X-TruncateLengthyTranscriptionsEnabled": get_or_default(test_data, Fields.TRUNCATE_LENGTHY_TRANSCRIPTIONS_ENABLED, "False"),
        "X-MaxTranscriptionLength": get_or_default(test_data, Fields.MAX_TRANSCRIPTION_LENGTH, "5000"),
        "X-MaxTranscriptionLineLength": get_or_default(test_data, Fields.MAX_TRANSCRIPTION_LINE_LENGTH, "900"),
        "X-LidEnabled": get_or_default(test_data, Fields.LID_ENABLED, "False"),
        "X-LidMode": get_or_default(test_data, Fields.LID_MODE, "AtStartHighAccuracy"),
        "X-ProfanityOption": get_or_default(test_data, AcsFields.PROFANITY_OPTION, "Masked"),
        "X-TaggingEnabled": get_or_default(test_data, AcsFields.TAGGING_ENABLED, "False"),
        "X-TagValue": get_or_default(test_data, AcsFields.TAG_VALUE, "tag value")
    }

    if extra_headers:
        headers.update(extra_headers)
    return headers

def get_smtp_default_headers():
    headers = {
        "Message-Id": "V2TIC Conversion",
        "X-Reference": "20230519004356-epsvaibhav-4130-91405",
        "Reply-To": "replyto@nuance.com",
        "callingNumberWithheld": "False",
        "Subject": "Test email",
        "Delivered-To": "193967777",
        "From": "11111111",
        "respondWithAudio": "False",
        "Content-Transfer-Encoding": "base64"
    }

    return headers