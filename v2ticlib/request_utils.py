#!/usr/bin/env python
# coding: utf-8
# Copyright (c) Microsoft. All rights reserved.
# Licensed under the MIT license. See LICENSE.md file in the project root for full license information.



from datetime import datetime
import v2ticlib.constants.fields as Fields
import v2ticlib.scrid_utils as scrid_utils
import v2ticlib.constants.fields as Fields
import v2ticlib.constants.constants as Constants
import v2ticlib.string_utils as string_utils
import v2ticlib.metadata_utils as metadata_utils
from functools import partial
import ast

def get_scrid(request:dict) -> str:
    return request[Fields.SCRID]

def get_deposit_time(request:dict) -> datetime:
    return request[Fields.DEPOSIT_TIME]

def get_status(request:dict) -> str:
    return request[Fields.STATUS]

def set_status(request:dict, status:str):
    request[Fields.STATUS] = status

def is_status_success(request:dict) -> bool:
    return get_status(request) == Constants.SUCCESS

def generate_initial_request_content():
    initial_request_content = {}
    initial_request_content[Fields.SCRID] = scrid_utils.generate_scrid()
    initial_request_content[Fields.DEPOSIT_TIME] = datetime.now()
    initial_request_content[Fields.NOTES] = {}
    initial_request_content[Fields.STATUS] = Constants.PENDING
    return initial_request_content

def does_not_have_notes_from_request(request:dict) -> bool:
    return not has_notes(request)

def has_notes(request:dict) -> bool:
    notes = request.get(Fields.NOTES)
    return notes != None and len(notes) > 0

def add_skip_note(request:dict, component:str):
    skip_note = f'{Constants.SKIPPING} {component} ...'
    add_notes(request, component, skip_note)

def add_notes(request, component, note):
    note_to_add:str = note
    notes:dict = request[Fields.NOTES]
    existing_note:str = notes.get(component)
    if string_utils.is_not_blank(existing_note):
        note_to_add = f'{existing_note}. {note}'
    notes[component] = note_to_add

def set_request_fields_if_not_exist(request:dict, initial_request_content:dict):
    for key,val in initial_request_content.items():
        if request.get(key) == None:
            request[key] = val

def create_metadata_if_not_exist(request:dict):
    if request.get(Fields.METADATA) == None:
        request[Fields.METADATA] = {}

def update_metadata_fields_if_not_exist(request:dict, metadata:dict):
    create_metadata_if_not_exist(request)
    request_metadata:dict = request[Fields.METADATA]
    for key,val in metadata.items():
        if request_metadata.get(key) == None:
            request_metadata[key] = val

def set_field(request:dict, field:str, obj:any):
    metadata:dict = request[Fields.METADATA]
    metadata[field] = obj

def get_field(request:dict, field:str, literal_eval=False) -> any:
    metadata:dict = request[Fields.METADATA]
    field_value = metadata.get(field)
    return do_get_field(field_value, literal_eval)

def do_get_field(field_value, literal_eval=False):
    if field_value is None:
        return None
    if type(field_value) == str and string_utils.is_blank(field_value):
        return None
    if literal_eval == False:
        return field_value
    return ast.literal_eval(field_value)

def get_language_field(request:dict) -> str:
    return get_field(request, Fields.LANGUAGE)

def get_language_configuration(request:dict) -> dict:
    return get_field(request, Fields.LANGUAGE_CONFIGURATION)

def get_acs_client(request:dict) -> dict:
    return get_field(request, Fields.ACS_CLIENT)

def does_not_have_audio(request:dict) -> bool:
    audio:bytes = request.get(Fields.AUDIO)
    return audio is None or audio == b''

def set_headers(request:dict, headers):
    request[Fields.HEADERS] = headers

def set_audio(request:dict, audio:bytes):
    request[Fields.AUDIO] = audio

def get_audio(request:dict) -> bytes:
    return request[Fields.AUDIO]

def set_audio_info(request:dict, audio_info:dict):
    set_field(request, Fields.AUDIO_INFO, audio_info)

def is_lid_enabled(request:dict) -> bool:
    return get_field(request, Fields.LID_ENABLED)

def get_requested_languages(request:dict) -> list:
    return get_field(request, Fields.REQUESTED_LANGUAGES)

def get_audio_info(request:dict) -> dict:
    return get_field(request, Fields.AUDIO_INFO)

def is_audio_truncated(request:dict) -> bool:
    audio_info = get_audio_info(request)
    return audio_info[Fields.AUDIO_TRUNCATED]

def get_audio_length(request:dict) -> float:
    audio_info = get_audio_info(request)
    audio_length:float = audio_info[Fields.DURATION]
    return audio_length

def get_max_audio_length_secs(request:dict) -> int:
    return get_field(request, Fields.MAX_AUDIO_LENGTH_SECS)

def get_min_confidence_percentage(request:dict) -> int:
    return get_field(request, Fields.MIN_CONFIDENCE_PERCENTAGE)

def get_recognition_result(request:dict) -> dict:
    return request[Fields.RECOGNITION_RESULT]

def set_recognition_result(request:dict, recognition_result:dict):
    request[Fields.RECOGNITION_RESULT] = recognition_result

def get_delivery_type(request:dict) -> str:
    return request[Fields.DELIVERY_TYPE]

def get_field_value_or_default(request:dict, field:str, default_func, literal_eval=False) -> any:
    field_value = get_field(request, field, literal_eval)
    if field_value is None:
        field_value = default_func()
    return field_value

def get_max_transcription_length(request:dict) -> int:
    default_func = partial(metadata_utils.get_default_max_transcription_length)
    return get_field_value_or_default(request, Fields.MAX_TRANSCRIPTION_LENGTH, default_func, literal_eval=True)

def is_log_transcriptions_enabled(request:dict) -> bool:
    default_func = partial(metadata_utils.is_log_transcriptions_enabled)
    return get_field_value_or_default(request, Fields.LOG_TRANSCRIPTIONS_ENABLED, default_func, literal_eval=True)

def is_truncate_lenghty_transcriptions_enabled(request:dict) -> bool:
    default_func = partial(metadata_utils.is_truncate_lenghty_transcriptions_enabled)
    return get_field_value_or_default(request, Fields.TRUNCATE_LENGTHY_TRANSCRIPTIONS_ENABLED, default_func, literal_eval=True)

def get_acs_client_property(request:dict, field, literal_eval=False):
    acs_client:dict = get_acs_client(request)
    if acs_client is None:
        return None
    value = acs_client.get(field)
    return do_get_field(value, literal_eval)

def respond_with_audio_enabled(request:dict) -> bool:
    default_func = partial(metadata_utils.respond_with_audio_enabled)
    return get_field_value_or_default(request, Fields.RESPOND_WITH_AUDIO_ENABLED, default_func, literal_eval=True)

def get_original_audio(request:dict) -> str:
    return get_field(request, Fields.ORIGINAL_AUDIO)

def set_original_audio(request:dict, encoded_audio:str):
    set_field(request, Fields.ORIGINAL_AUDIO, encoded_audio)

def get_max_transcription_line_length(request:dict) -> int:
    default_func = partial(metadata_utils.get_max_transcription_line_length)
    return get_field_value_or_default(request, Fields.MAX_TRANSCRIPTION_LINE_LENGTH, default_func, literal_eval=True)

def is_conversion_status_timeout(request):
    recognition_result:dict = request[Fields.RECOGNITION_RESULT]
    conversion_status = recognition_result.get(Fields.CONVERSION_STATUS)
    return conversion_status == Constants.TIMEDOUT

def set_speech_resource(request, speech_resource):
    set_field(request, Fields.SPEECH_RESOURCE, speech_resource)

def get_speech_resource(request):
    return get_field(request, Fields.SPEECH_RESOURCE)