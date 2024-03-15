#!/usr/bin/env python
# coding: utf-8
# Copyright (c) Microsoft. All rights reserved.
# Licensed under the MIT license. See LICENSE.md file in the project root for full license information.



import azure.cognitiveservices.speech as speechsdk
from v2ticlib.logger_utils import log, debug, CONTEXT
import v2ticlib.constants.fields as Fields
from AcsClient.acs_client import AcsClient
import json
import v2ticlib.metadata_utils as metadata_utils
import v2ticlib.constants.constants as Constants

class AcsClientLid(AcsClient):
    def get_lid_mode(self, request):
        return self.get_runtime_property(request, Fields.LID_MODE)
    
    def get_lid_type(self):
        return self.get_property(Fields.LID_TYPE)

    def log_speech_config_details(self, request):
        speech_config_dict = self.get_speech_config_details(request)
        speech_config_dict[Fields.LID_ENABLED] = True
        lid_mode = self.get_lid_mode(request)
        speech_config_dict[Fields.LID_MODE] = lid_mode
        self.do_log_speech_config_details(speech_config_dict)

    def get_speech_config(self, request):
        speech_config = super().get_speech_config(request)
        if self.get_lid_type() == Constants.LID_FALLBACK:
            default_lid_fallback_language = metadata_utils.get_default_lid_fallback_language()
            speech_config.set_service_property(name="SpeechContext-phraseDetection.language", value=default_lid_fallback_language, channel=speechsdk.ServicePropertyChannel.UriQueryParameter)
            log(f'Using lid_fallback language = {default_lid_fallback_language} for Language identification transcription')
        else:
            lid_mode = self.get_lid_mode(request)
            speech_config.set_property(property_id=speechsdk.PropertyId.SpeechServiceConnection_LanguageIdMode, value=lid_mode)
            log(f'Using lid_mode = {lid_mode} for Language identification transcription')
        return speech_config

    def handle_timeout(self, request, recognition_result):
        recognition_result[Fields.DETECTED_LANGUAGES] = ''
        super().handle_timeout(request, recognition_result)

    def do_do_transcribe(self, scrid, languages, audio_config, timeout, recognition_result, speech_config):
        recognition_result[Fields.DETECTED_LANGUAGES] = []
        self.recognize_multi_language(scrid, languages, audio_config, timeout, recognition_result, speech_config)
        recognition_result[Fields.DETECTED_LANGUAGES] = self.join_languages(recognition_result[Fields.DETECTED_LANGUAGES])

    def append_detected_language(self, recognition_result:dict, detected_language:str):
        detected_languages: list = recognition_result[Fields.DETECTED_LANGUAGES]
        if len(detected_languages) == 0:
            detected_languages.append(detected_language)
            return

        last_detected_language = detected_languages[-1]
        if last_detected_language != detected_language:
            detected_languages.append(detected_language)

    def recognize_multi_language(self, scrid, languages, audio_config, timeout, recognition_result, speech_config):
        log(f'recognize_multi_language: {languages}')
        auto_detect_source_language_config = speechsdk.languageconfig.AutoDetectSourceLanguageConfig(languages=languages)
        speech_recognizer = speechsdk.SpeechRecognizer(speech_config=speech_config,
                                                    audio_config=audio_config,
                                                    auto_detect_source_language_config=auto_detect_source_language_config)

        def recognized_cb(evt: speechsdk.SpeechRecognitionEventArgs):
            CONTEXT.set(scrid)
            if evt.result.reason == speechsdk.ResultReason.RecognizedSpeech:
                debug(f'RECOGNIZED: {evt.result.properties}')
                if evt.result.properties.get(
                        speechsdk.PropertyId.SpeechServiceConnection_AutoDetectSourceLanguageResult) is None:
                    log("Unable to detect any language")
                else:
                    detected_language = evt.result.properties[
                        speechsdk.PropertyId.SpeechServiceConnection_AutoDetectSourceLanguageResult]

                    log(f'Detected language = {detected_language}')
                    self.append_detected_language(recognition_result, detected_language)
                    self.update_recognition_result(recognition_result, evt)

        if self.get_lid_type() == Constants.LID_FALLBACK:
            self.do_recognize_multi_language_fallback(scrid, speech_recognizer, recognized_cb, timeout, languages)
            return

        self.do_recognize(scrid, speech_recognizer, recognized_cb, timeout)

    def do_recognize_multi_language_fallback(self, scrid, speech_recognizer, recognized_cb, timeout, languages):
        connection:speechsdk.Connection = speechsdk.Connection.from_recognizer(speech_recognizer)
        connection.set_message_property("speech.context", "LanguageId", self.get_language_id_payload(languages))
        try:
            self.do_recognize(scrid, speech_recognizer, recognized_cb, timeout)
        finally:
            try:
                connection.close()
            except Exception as e:
                log(f'Error closing speech recognizer connection: {e}')

    def get_language_id_payload(self, languages):
        payload = self.get_property("language_id_json", literal_eval=True)
        payload["Languages"] = languages
        payload_string = json.dumps(payload)
        log(f'Speech Context for LID fallback feature: {payload_string}')
        return payload_string