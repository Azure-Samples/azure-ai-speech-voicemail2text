import typing
from base64 import b64encode, b64decode, encodebytes
from Common.request_validator import RequestValidator
from v2ticlib.template_utils import template_utils
import v2ticlib.language_configuration_utils as language_configuration_utils
import v2ticlib.request_utils as request_utils

class RequestInjestor():
    def __init__(self):
        self._request_validator = RequestValidator()

    def injest(self, initial_request_content:dict, headers:typing.Mapping[str, str], body:bytes):
        request = template_utils.render_request(initial_request_content, headers)
        language_configuration_utils.resolve(request)
        self.resolve_audio(request, body)
        self._request_validator.validate(request)
        return request

    def resolve_audio(self, request:dict, body:bytes):
        audio_bytes = self.get_audio_bytes(body)
        request_utils.set_audio(request, audio_bytes)
        if request_utils.respond_with_audio_enabled(request):
            audio_string = str(encodebytes(audio_bytes), 'ascii')
            request_utils.set_original_audio(request, audio_string)

    def get_audio_bytes(self, body:bytes):
        if self.is_base64_encoded(body):
            return b64decode(body)
        else:
            return body

    def is_base64_encoded(self, body:bytes):
        try:
            str_body = str(body, 'ascii')
            str_stripped_body = str_body.replace('\n', '').replace('\r', '')
            stripped_body = str.encode(str_stripped_body, 'ascii')
            decoded = b64decode(stripped_body)
            encoded = b64encode(decoded)
            return encoded == stripped_body
        except Exception:
            return False
