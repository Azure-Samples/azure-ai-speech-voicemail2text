#!/usr/bin/env python
# coding: utf-8
# Copyright (c) Microsoft. All rights reserved.
# Licensed under the MIT license. See LICENSE.md file in the project root for full license information.



import os
import threading
import json
import azure.cognitiveservices.speech as speechsdk
from azure.cognitiveservices.speech.enums import ProfanityOption
from v2ticlib import config_utils
from v2ticlib.logger_utils import log, debug, CONTEXT
import v2ticlib.constants.fields as Fields
import v2ticlib.constants.constants as Constants
import v2ticlib.string_utils as string_utils
import v2ticlib.thread_pool_executor_utils as thread_pool_executor
import AcsClient.constants.constants as Acs_Constants
import AcsClient.constants.fields as Acs_Fields
from AcsClient.speech_resource_repository import speech_resource_repository
from AcsClient.speech_resource import SpeechResource
import v2ticlib.request_utils as request_utils

class AcsClient():

    def __init__(self):
        self._config_base = Acs_Constants.ACS_CLIENT

    def get_property(self, property, literal_eval=False):
        return config_utils.get_property(self._config_base, property, literal_eval=literal_eval)

    def get_runtime_property(self, request:dict, field, literal_eval=False):
        value = request_utils.get_acs_client_property(request, field, literal_eval)
        if value is not None:
            return value
        value = self.get_property(field, literal_eval)
        return value

    def get_default_language(self):
        return self.get_property("default_language")

    def get_default_languages(self):
        return self.get_property("default_languages", literal_eval=True)

    def get_audio_multiplier(self):
        return self.get_property("audio_multiplier", literal_eval=True)

    def get_profanity_option(self, request):
        profanity_option = self.get_runtime_property(request, Acs_Fields.PROFANITY_OPTION)
        return ProfanityOption[profanity_option]

    def get_word_level_confidence(self):
        return self.get_property("word_level_confidence")

    def get_display_word_timings(self):
        return self.get_property("display_word_timings")

    def use_default_silence_values(self):
        return self.get_property("silence.use_default_values", literal_eval=True)

    def get_initial_silence_timeout(self):
        timeout = config_utils.get_timelength_property_msecs(self._config_base, "silence.initial_silence_timeout")
        return str(round(timeout))

    def get_segment_silence_timeout(self):
        timeout = config_utils.get_timelength_property_msecs(self._config_base, "silence.segment_silence_timeout")
        return str(round(timeout))

    def get_segmentation_forced_timeout(self):
        timeout = config_utils.get_timelength_property_msecs(self._config_base, "segmentation_forced_timeout")
        return str(round(timeout))

    def get_hard_tat_handler(self):
        return self.get_property("hard_tat_handler", literal_eval=True)

    def is_tagging_enabled(self, request):
        return self.get_runtime_property(request, Acs_Fields.TAGGING_ENABLED, literal_eval=True)

    def get_tag_value(self, request):
        return self.get_runtime_property(request, Acs_Fields.TAG_VALUE)

    def is_sdk_logs_enabled(self):
        return self.get_property("sdk_logs.enabled", literal_eval=True)

    def get_sdk_log_filename(self):
        return self.get_property("sdk_logs.log_filename")

    def get_fail_safe_timeout(self):
        return config_utils.get_timelength_property_secs(self._config_base, "fail_safe_timeout")

    def get_endpoint(self, request):
        speech_resource:SpeechResource = request_utils.get_speech_resource(request)
        return speech_resource.endpoint

    def get_key(self, request):
        speech_resource:SpeechResource = request_utils.get_speech_resource(request)
        return speech_resource.key

    def get_speech_config_details(self, request) -> dict:
        speech_config = {}
        speech_config[Acs_Fields.PROFANITY_OPTION] = self.get_profanity_option(request)
        speech_config[Acs_Fields.WORD_LEVEL_CONFIDENCE] = self.get_word_level_confidence()
        speech_config[Acs_Fields.DISPLAY_WORD_TIMINGS] = self.get_display_word_timings()
        speech_config[Acs_Fields.SILENCE_USE_DEFAULT_VALUES] = self.use_default_silence_values()
        speech_config[Acs_Fields.SEGMENT_SILENCE_TIMEOUT] = self.get_segment_silence_timeout()
        speech_config[Acs_Fields.INITIAL_SILENCE_TIMEOUT] = self.get_initial_silence_timeout()
        speech_config[Acs_Fields.SEGMENTATION_FORCED_TIMEOUT] = self.get_segmentation_forced_timeout()
        speech_config[Acs_Fields.TAGGING_ENABLED] = self.is_tagging_enabled(request)
        speech_config[Acs_Fields.TAG_VALUE] = self.get_tag_value(request)
        speech_config[Acs_Fields.HARD_TAT_HANDLER] = self.get_hard_tat_handler()
        speech_config[Acs_Fields.SDK_LOGS_ENABLED] = self.is_sdk_logs_enabled()
        speech_config[Acs_Fields.SDK_LOG_FILENAME] = self.get_sdk_log_filename()
        speech_config[Acs_Fields.SPEECH_ENDPOINT] = self.get_endpoint(request)
        speech_config[Acs_Fields.POST_PROCESSING_OPTION] = Acs_Constants.TRUETEXT
        speech_config[Acs_Fields.OUTPUT_FORMAT] = speechsdk.OutputFormat.Detailed
        speech_config[Acs_Fields.PHRASE_DETECTION_MODE] = Acs_Constants.CONVERSATION
        speech_config[Acs_Fields.CONVERSATION_SEGMENTATION_MODE] = Acs_Constants.CUSTOM
        return speech_config

    def log_speech_config_details(self, request):
        speech_config_dict = self.get_speech_config_details(request)
        self.do_log_speech_config_details(speech_config_dict)

    def do_log_speech_config_details(self, speech_config_dict):
        log(f'{Acs_Fields.SPEECH_CONFIG} : {speech_config_dict}')

    def get_speech_config(self, request):
        speech_config_dict = self.get_speech_config_details(request)
        speech_config = speechsdk.SpeechConfig(endpoint=self.get_endpoint(request), subscription=self.get_key(request))
        speech_config.output_format = speech_config_dict[Acs_Fields.OUTPUT_FORMAT]
        speech_config.request_word_level_timestamps()
        speech_config.set_property(property_id=speechsdk.PropertyId.SpeechServiceResponse_PostProcessingOption, value=speech_config_dict[Acs_Fields.POST_PROCESSING_OPTION])
        speech_config.set_profanity(profanity_option=speech_config_dict[Acs_Fields.PROFANITY_OPTION])

        speech_config.set_service_property(name="wordLevelConfidence", value=speech_config_dict[Acs_Fields.WORD_LEVEL_CONFIDENCE], channel=speechsdk.ServicePropertyChannel.UriQueryParameter)
        speech_config.set_service_property(name="displayWordTimings", value=speech_config_dict[Acs_Fields.DISPLAY_WORD_TIMINGS], channel=speechsdk.ServicePropertyChannel.UriQueryParameter)

        if (speech_config_dict[Acs_Fields.SILENCE_USE_DEFAULT_VALUES] == False):
            speech_config.set_property(property_id=speechsdk.PropertyId.SpeechServiceConnection_InitialSilenceTimeoutMs, value=speech_config_dict[Acs_Fields.INITIAL_SILENCE_TIMEOUT])
            speech_config.set_service_property(name="SpeechContext-phraseDetection.conversation.segmentation.segmentationSilenceTimeoutMs", value=speech_config_dict[Acs_Fields.SEGMENT_SILENCE_TIMEOUT], channel=speechsdk.ServicePropertyChannel.UriQueryParameter)
            speech_config.set_service_property(name="SpeechContext-phraseDetection.mode", value=speech_config_dict[Acs_Fields.PHRASE_DETECTION_MODE], channel=speechsdk.ServicePropertyChannel.UriQueryParameter)
            speech_config.set_service_property(name="SpeechContext-phraseDetection.conversation.segmentation.mode", value=speech_config_dict[Acs_Fields.CONVERSATION_SEGMENTATION_MODE], channel=speechsdk.ServicePropertyChannel.UriQueryParameter)
            speech_config.set_service_property(name="SpeechContext-phraseDetection.conversation.segmentation.segmentationForcedTimeoutMs", value=speech_config_dict[Acs_Fields.SEGMENTATION_FORCED_TIMEOUT], channel=speechsdk.ServicePropertyChannel.UriQueryParameter)
        else:
            speech_config_dict.pop(Acs_Fields.INITIAL_SILENCE_TIMEOUT)
            speech_config_dict.pop(Acs_Fields.SEGMENT_SILENCE_TIMEOUT)
            speech_config_dict.pop(Acs_Fields.PHRASE_DETECTION_MODE)
            speech_config_dict.pop(Acs_Fields.CONVERSATION_SEGMENTATION_MODE)
            speech_config_dict.pop(Acs_Fields.SEGMENTATION_FORCED_TIMEOUT)

        if (speech_config_dict[Acs_Fields.HARD_TAT_HANDLER]):
            speech_config.set_service_property(name="setFeature", value="srturnendflt", channel=speechsdk.ServicePropertyChannel.UriQueryParameter)

        if (speech_config_dict[Acs_Fields.SDK_LOGS_ENABLED]):
            sdk_log_file = os.path.join(os.path.abspath(os.curdir), speech_config_dict[Acs_Fields.SDK_LOG_FILENAME])
            speech_config.set_property(speechsdk.PropertyId.Speech_LogFilename, value=sdk_log_file)
        else:
            speech_config_dict.pop(Acs_Fields.SDK_LOG_FILENAME)

        if (speech_config_dict[Acs_Fields.TAGGING_ENABLED]):
            speech_config.set_service_property(name="trafficType", value=speech_config_dict[Acs_Fields.TAG_VALUE], channel=speechsdk.ServicePropertyChannel.UriQueryParameter)
        else:
            speech_config_dict.pop(Acs_Fields.TAG_VALUE)

        return speech_config

    def get_max_timeout(self, request):
        return self.get_audio_multiplier() * request_utils.get_audio_length(request)

    def join_languages(self, languages:list):
        return ", ".join(languages)

    async def transcribe(self, request):
        try:
            speech_resource = speech_resource_repository.get_speech_resource()
            log(f'Using speech resource: {speech_resource}')
            request_utils.set_speech_resource(request, speech_resource)
            timeout = self.get_max_timeout(request) + self.get_fail_safe_timeout()
            await thread_pool_executor.run_executor_async_with_timeout(timeout, self._config_base, self.do_transcribe, request)
        except Exception as e:
            log(f'Caught exception during transcription: {str(e)}')
            raise e

    def finalize_recognition_result(self, request, recognition_result):
        if (len(recognition_result[Fields.TEXT]) > 0):
            recognition_result[Fields.WEIGHTED_CONFIDENCE] = recognition_result[Fields.CONFIDENCE] / recognition_result[Fields.DURATION]

        recognition_result[Fields.TEXT] = self.join_recognition_text(recognition_result[Fields.TEXT])
        recognition_result[Fields.DISPLAY_TEXT] = self.join_recognition_text(recognition_result[Fields.DISPLAY_TEXT])
        recognition_result[Fields.ITN_TEXT] = self.join_recognition_text(recognition_result[Fields.ITN_TEXT])

        recognition_result[Fields.GLOBAL_CONFIDENCE_SCORE] = round(recognition_result[Fields.WEIGHTED_CONFIDENCE]*100, 1)
        request_utils.set_recognition_result(request, recognition_result)

    def join_recognition_text(self, texts:list):
        text = " ".join(texts)
        return text.strip()

    def get_audio_config(self, request):
        stream = speechsdk.audio.PushAudioInputStream()
        audio_bytes = request_utils.get_audio(request)
        stream.write(audio_bytes)
        stream.close()
        return speechsdk.audio.AudioConfig(stream=stream)

    def get_recognition_result_object(self):
        recognition_result = {}
        recognition_result[Fields.TEXT] = []
        recognition_result[Fields.DISPLAY_TEXT] = []
        recognition_result[Fields.ITN_TEXT] = []
        recognition_result[Fields.DURATION] = 0
        recognition_result[Fields.CONFIDENCE] = 0
        recognition_result[Fields.WEIGHTED_CONFIDENCE] = 0
        recognition_result[Fields.STATUS] = ''
        return recognition_result

    def update_recognition_result(self, recognition_result, evt: speechsdk.SpeechRecognitionEventArgs):
        json_result = evt.result.properties.get(speechsdk.PropertyId.SpeechServiceResponse_JsonResult)
        json_object = json.loads(json_result)

        text = evt.result.text
        display_text = json_object['DisplayText']
        duration = json_object['Duration'] / 10000000
        nbest = json_object.get('NBest')
        itn_text = nbest[0]['ITN']
        confidence = nbest[0]['Confidence']

        recognition_result[Fields.STATUS] = json_object['RecognitionStatus']
        self.update_recognition_text(recognition_result[Fields.TEXT], text)
        self.update_recognition_text(recognition_result[Fields.DISPLAY_TEXT], display_text)
        self.update_recognition_text(recognition_result[Fields.ITN_TEXT], itn_text)
        recognition_result[Fields.DURATION] = recognition_result[Fields.DURATION] + duration
        recognition_result[Fields.CONFIDENCE] = recognition_result[Fields.CONFIDENCE] +  duration*confidence

    def update_recognition_text(self, field:list, text:str):
        if string_utils.is_blank(text):
            return
        field.append(text)

    def do_transcribe(self, request):
        scrid = request_utils.get_scrid(request)
        CONTEXT.set(scrid)

        audio_config = self.get_audio_config(request)
        self.log_speech_config_details(request)
        speech_config = self.get_speech_config(request)
        languages:list = request_utils.get_requested_languages(request)

        recognition_result = self.get_recognition_result_object()

        recognition_result[Fields.FINAL_AUDIO_LENGTH_SECS] = request_utils.get_audio_length(request)
        recognition_result[Fields.FINAL_AUDIO_LENGTH_MSECS] = int(round(recognition_result[Fields.FINAL_AUDIO_LENGTH_SECS]*1000, 1))
        recognition_result[Fields.LID_ENABLED] = request_utils.is_lid_enabled(request)
        recognition_result[Fields.REQUESTED_LANGUAGES] = self.join_languages(languages)
        timeout = self.get_max_timeout(request)

        try:
            self.do_do_transcribe(scrid, languages, audio_config, timeout, recognition_result, speech_config)
            self.finalize_recognition_result(request, recognition_result)
        except TimeoutError as timeout_error:
            log(f'Caught timeout error: {str(timeout_error)}')
            self.handle_timeout(request, recognition_result)
        except Exception as exception:
            raise exception

    def handle_timeout(self, request, recognition_result):
        recognition_result[Fields.CONVERSION_STATUS] = Constants.TIMEDOUT
        recognition_result[Fields.TEXT] = ''
        recognition_result[Fields.DISPLAY_TEXT] = ''
        recognition_result[Fields.ITN_TEXT] = ''
        recognition_result[Fields.GLOBAL_CONFIDENCE_SCORE] = 0
        request_utils.set_recognition_result(request, recognition_result)

    def do_do_transcribe(self, scrid, languages, audio_config, timeout, recognition_result, speech_config):
        language = languages[0]
        self.recognize_single_language(scrid, language, audio_config, timeout, recognition_result, speech_config)

    def recognize_single_language(self, scrid, language, audio_config, timeout, recognition_result, speech_config):

        log(f'recognize_single_language: {language}')
        speech_recognizer = speechsdk.SpeechRecognizer(speech_config=speech_config, audio_config=audio_config, language=language)

        def recognized_cb(evt: speechsdk.SpeechRecognitionEventArgs):
            CONTEXT.set(scrid)
            debug(f'RECOGNIZED: {evt}')
            self.update_recognition_result(recognition_result, evt)

        self.do_recognize(scrid, speech_recognizer, recognized_cb, timeout)

    def do_recognize(self, scrid, speech_recognizer: speechsdk.SpeechRecognizer, recognized_cb, timeout):

        result_available = threading.Event()

        def recognizing_cb(evt: speechsdk.SessionEventArgs):
            CONTEXT.set(scrid)
            debug(f'RECOGNIZING on {evt}')

        def session_started_cb(evt: speechsdk.SessionEventArgs):
            CONTEXT.set(scrid)
            debug(f'SESSION_STARTED on {evt}')

        def cancelled_cb(evt: speechsdk.SpeechRecognitionCanceledEventArgs):
            CONTEXT.set(scrid)
            debug(f'CANCELLED on {evt}')
            if (evt.result.reason == speechsdk.ResultReason.Canceled):
                log(f'setting flag to True')
                result_available.set()

        def stop_cb(evt: speechsdk.SessionEventArgs):
            CONTEXT.set(scrid)
            debug(f'CLOSING on {evt}')
            log(f'setting flag to True')
            result_available.set()

        speech_recognizer.recognizing.connect(recognizing_cb)
        speech_recognizer.recognized.connect(recognized_cb)
        speech_recognizer.session_started.connect(session_started_cb)
        speech_recognizer.session_stopped.connect(stop_cb)
        speech_recognizer.canceled.connect(cancelled_cb)

        log(f'setting wait timeout to: {timeout} seconds')

        speech_recognizer.start_continuous_recognition()
        log('called start_continuous_recognition')

        signaled = result_available.wait(timeout)
        try:
            if signaled is False:
                log('timed out waiting for recognition to finish')
                raise TimeoutError(f'timed out waiting for recognition to finish after {timeout} seconds')
        finally:
            log('calling stop_continuous_recognition')
            speech_recognizer.stop_continuous_recognition()
            log('called stop_continuous_recognition')