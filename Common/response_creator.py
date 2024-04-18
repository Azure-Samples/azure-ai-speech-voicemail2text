#!/usr/bin/env python
# coding: utf-8
# Copyright (c) Microsoft. All rights reserved.
# Licensed under the MIT license. See LICENSE.md file in the project root for full license information.


from v2ticlib.template_utils import template_utils
from v2ticlib.logger_utils import log
import v2ticlib.constants.fields as Fields
import v2ticlib.constants.constants as Constants
import v2ticlib.string_utils as string_utils
import v2ticlib.rtf_utils as rtf_utils
import v2ticlib.request_utils as request_utils
import textwrap

class ResponseCreator():
    transcription_text_fields = [Fields.TEXT, Fields.DISPLAY_TEXT, Fields.ITN_TEXT]

    def create(self, request):
        status = Constants.FAILED
        if request_utils.does_not_have_notes_from_request(request):
            self.update_recognition_result(request)
            status = Constants.SUCCESS
        request_utils.set_status(request, status)
        updated_request = request_utils.update_request_with_escaped_values(request)
        return template_utils.render_response(updated_request)

    def update_recognition_result(self, request):
        recognition_result:dict = request_utils.get_recognition_result(request)

        self.resolve_truncated_audio(request, recognition_result)

        self.resolve_conversion_status(request, recognition_result)

        self.resolve_text_truncation(request, recognition_result)

        self.resolve_rtf(request, recognition_result)

        self.resolve_respond_with_audio_enabled(request, recognition_result)

        self.resolve_transcription_text_wrapping(request, recognition_result)

        self.resolve_logging_transcription(request, recognition_result)

        request_utils.set_recognition_result(request, recognition_result)

    def resolve_truncated_audio(self, request:dict, recognition_result:dict):
        truncated = Constants.FALSE
        if request_utils.is_audio_truncated(request):
            truncated = Constants.TRUE
        recognition_result[Fields.AUDIO_TRUNCATED] = truncated

    def resolve_conversion_status(self, request:dict, recognition_result:dict):
        if self.has_conversion_status(recognition_result):
            return

        min_confidence_percentage = request_utils.get_min_confidence_percentage(request)
        recognition_result[Fields.CONVERSION_STATUS] = self.get_conversion_status(recognition_result, min_confidence_percentage)
        if recognition_result[Fields.CONVERSION_STATUS] == Constants.UNCONVERTIBLE:
            log(f'recognition was found as {Constants.UNCONVERTIBLE}')
            recognition_result[Fields.TEXT] = ''
            recognition_result[Fields.DISPLAY_TEXT] = ''
            recognition_result[Fields.ITN_TEXT] = ''

    def has_conversion_status(self, recognition_result:dict):
        return string_utils.is_not_blank(recognition_result.get(Fields.CONVERSION_STATUS))

    def get_conversion_status(self, recognition_result:dict, min_confidence_percentage:int):
        if string_utils.is_blank(recognition_result[Fields.TEXT]):
            log('blank recognition result text')
            return Constants.UNCONVERTIBLE

        confidence_percentage = recognition_result[Fields.GLOBAL_CONFIDENCE_SCORE]
        if confidence_percentage < min_confidence_percentage:
            log(f'global confidence score [{confidence_percentage}] is lower than min confidence percentage [{min_confidence_percentage}]')
            return Constants.UNCONVERTIBLE

        return Constants.TRANSCRIBED

    def resolve_text_truncation(self, request:dict, recognition_result:dict):
        if recognition_result[Fields.CONVERSION_STATUS] != Constants.TRANSCRIBED:
            return

        if request_utils.is_truncate_lenghty_transcriptions_enabled(request) == False:
            return

        max_transcription_length = request_utils.get_max_transcription_length(request)
        for field in self.transcription_text_fields:
            self.do_truncate_text(recognition_result, field, max_transcription_length)

    def do_truncate_text(self, recognition_result:dict, field:str, max_transcription_length:int):
        transcription_text = recognition_result[field]
        if(len(transcription_text) > max_transcription_length):
            recognition_result[field] = transcription_text[:max_transcription_length]

    def resolve_rtf(self, request:dict, recognition_result:dict):
        deposit_time = request_utils.get_deposit_time(request)
        recognition_result[Fields.RTF] = rtf_utils.get_rtf(deposit_time, recognition_result[Fields.FINAL_AUDIO_LENGTH_SECS])

    def resolve_respond_with_audio_enabled(self, request:dict, recognition_result:dict):
        respond_with_audio_enabled:bool = request_utils.respond_with_audio_enabled(request)
        recognition_result[Fields.RESPOND_WITH_AUDIO_ENABLED] = respond_with_audio_enabled
        if respond_with_audio_enabled:
            recognition_result[Fields.ORIGINAL_AUDIO] = request_utils.get_original_audio(request)

    def resolve_transcription_text_wrapping(self, request:dict, recognition_result:dict):
        if recognition_result[Fields.CONVERSION_STATUS] != Constants.TRANSCRIBED:
            return

        max_transcription_line_length = request_utils.get_max_transcription_line_length(request)
        for field in self.transcription_text_fields:
            value = recognition_result[field]
            recognition_result[field] = textwrap.fill(text=value, width=max_transcription_line_length)

    def resolve_logging_transcription(self, request:dict, recognition_result:dict):
        log_transcriptions_enabled:bool = request_utils.is_log_transcriptions_enabled(request)

        recognition_result_to_log = self.update_recognition_result_for_logging(recognition_result,
                                                self.transcription_text_fields, log_transcriptions_enabled)

        recognition_result_to_log = self.update_recognition_result_for_logging(recognition_result_to_log,
                                                [Fields.ORIGINAL_AUDIO], logging_enabled=False)

        log(f'Recognition Results: {recognition_result_to_log}')

    def update_recognition_result_for_logging(self, recognition_result:dict, fields:list, logging_enabled:bool):
        recognition_result_to_log = recognition_result
        if(logging_enabled == False):
            recognition_result_to_log = {key:('**not logging private content**' if key in fields else val) for (key, val) in recognition_result.copy().items()}
        return recognition_result_to_log