import os, sys, typing, ssl
import asyncio
import email
from email.message import EmailMessage
from aiosmtpd.controller import Controller
sys.path.append(os.path.join(os.path.abspath(os.curdir)))
from v2ticlib.logger_utils import log, CONTEXT
import Common.request_handler as request_handler
from Common.request_injestor import RequestInjestor
from Common.Smtp.after_deposit_ack_handler import AfterDepositAckHandler
from v2ticlib import config_utils
from v2ticlib.constants.protocols import SMTP
from v2ticlib.constants.fields import SCRID, DELIVERY_TYPE
from v2ticlib.constants.headers import FROM, TO
from v2ticlib.template_utils import template_utils
import v2ticlib.coroutine_timeout_utils as coroutine_timeout
import v2ticlib.request_utils as request_utils
import v2ticlib.ssl_context_utils as ssl_context_utils

consume_request_timeout = config_utils.get_consume_request_timeout()
global keep_server_alive
keep_server_alive:bool = True

class SMTPHandler():
    def __init__(self):
        self._config_base = SMTP
        self._injestor = RequestInjestor()
        self._after_deposit_ack_handler = AfterDepositAckHandler()

    def get_property(self, property, literal_eval=False):
        return config_utils.get_property(self._config_base, property, literal_eval=literal_eval)

    def is_after_deposit_ack_enabled(self):
        return template_utils.has_after_deposit_ack_template()

    def get_default_return_code(self):
        return self.get_property('default_return_code')

    def get_return_code(self, request):
        return_code:str = self.get_default_return_code()
        if template_utils.has_smtp_return_code_template():
            return_code = template_utils.render_smtp_return_code(request)

        return return_code

    async def handle_DATA(self, server, session, envelope):
        initial_request_content:dict = request_utils.generate_initial_request_content()
        initial_request_content[DELIVERY_TYPE] = SMTP
        CONTEXT.set(initial_request_content[SCRID])

        mail_from = envelope.mail_from
        mail_to = envelope.rcpt_tos
        log(f'Received message From: {mail_from} with To: {mail_to}')

        try:
            return await coroutine_timeout.timeout_after(self.do_handle_DATA(initial_request_content, mail_from, mail_to, envelope), timeout=consume_request_timeout)
        except Exception as e:
            raise e

    async def do_handle_DATA(self, initial_request_content:dict, mail_from, mail_to, envelope):
        email_message: EmailMessage = email.message_from_bytes(envelope.content)
        headers = dict(email_message.items())
        headers[FROM] = mail_from
        headers[TO] = mail_to

        audio_bytes = None
        if email_message.is_multipart():
            audio_bytes = self.parse_multipart_request(email_message)
        else:
            audio_bytes = self.parse_simple_request(email_message)

        try:
            request = self.handle_request(initial_request_content, headers, audio_bytes)
        except Exception as e:
            raise e

        return_code = self.get_return_code(request)
        log(f'Returning: {return_code}')
        return return_code

    def parse_multipart_request(self, email_message:EmailMessage):
        message_bytes = b''
        for message in email_message.get_payload():
            bytes_data = message.get_payload(decode=True)
            message_bytes = message_bytes + bytes_data
        return message_bytes

    def parse_simple_request(self, email_message:EmailMessage):
        message_payload_type = type(email_message.get_payload())
        message_bytes = None
        if(message_payload_type is str):
            message_bytes = email_message.get_payload(decode=True)
        else:
            raise Exception(f'Unknown payload type {message_payload_type}')
        return message_bytes

    def handle_request(self, metadata:dict, headers: typing.Mapping[str, str], body: bytes):
        request = self._injestor.injest(metadata, headers, body)

        if self.is_after_deposit_ack_enabled():
            asyncio.create_task(self.handle_after_deposit_ack(request))

        asyncio.create_task(self.process_request(request))

        return request

    async def process_request(self, request):
        scrid = request_utils.get_scrid(request)
        CONTEXT.set(scrid)
        await request_handler.process_request(request)

    async def handle_after_deposit_ack(self, request):
        scrid = request_utils.get_scrid(request)
        CONTEXT.set(scrid)
        await self._after_deposit_ack_handler.send_acknowledgement(request)

async def start_smtp_server():
    host = config_utils.get_host()
    port = config_utils.get_port()
    ssl_context = ssl_context_utils.create_server_ssl_context()

    handler = SMTPHandler()
    controller = Controller(handler, hostname=host, port=port, tls_context=ssl_context)
    print(f'SMTP Server Listening On: {host}:{port}')
    controller.start()

    # Keep the server running
    while keep_server_alive:
        await asyncio.sleep(1)

def stop_server():
    global keep_server_alive
    keep_server_alive = False

if __name__ == "__main__":
    asyncio.run(start_smtp_server())