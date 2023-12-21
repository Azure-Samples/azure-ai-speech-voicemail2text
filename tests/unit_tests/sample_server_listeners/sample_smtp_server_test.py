#!/usr/bin/env python
# coding: utf-8
# Copyright (c) Microsoft. All rights reserved.
# Licensed under the MIT license. See LICENSE.md file in the project root for full license information.

import unittest
from unittest.mock import MagicMock, patch, call
import ssl, sys, os
import pytest
sys.path.append(os.path.join(os.path.abspath(os.curdir)))
import sample_server_listeners.sample_smtp_server as SampleSMTPServer
from sample_server_listeners.sample_smtp_server import SimpleSMTPRequestHandler as SimpleSampleSMTPServer

def read_audio_file(audio_file_path: str) -> bytes:
    with open(audio_file_path, "rb") as audio_file:
        audio_data = audio_file.read()
        return audio_data

class TestSampleSMTPServer(unittest.TestCase):
    @pytest.mark.asyncio
    async def test_handle_SMTP_request_AC8(self):
        server = MagicMock()
        session = MagicMock()
        envelope = MagicMock()
        with patch('builtins.print') as mock_print:
            mock_print.return_value = None
            envelope.mail_from = "sender@example.com"
            envelope.rcpt_tos = ["recipient1@example.com", "recipient2@example.com"]
            # envelope.content = b"This is a test message"
            envelope.content = read_audio_file("etc/audio/sample-audio-en-US-short.txt")
            result = await SimpleSampleSMTPServer.handle_DATA(server, session, envelope)
            #assert SMTP server response message and status code - AC8
            assert mock_print.call_args_list == [call("Received message:"), call(f'From: {envelope.mail_from}'), call(f'To: {envelope.rcpt_tos}'), call("-----------------------"), call(f'Message data:{os.linesep}{envelope.content.decode()}')]
            self.assertEqual(result, "250 OK")

    async def test_handle_SMTP_request_exception_AC9(self):
        server = MagicMock()
        session = MagicMock()
        envelope = MagicMock()
        with patch('builtins.print') as mock_print, \
             patch('sample_smtp_server.SimpleSMTPRequestHandler.get_charset') as mock_get_charset:
            mock_print.return_value = None
            envelope.mail_from = "sender@example.com"
            envelope.rcpt_tos = ["recipient1@example.com", "recipient2@example.com"]
            # envelope.content = b"This is a test message"
            envelope.content = read_audio_file("etc/audio/sample-audio-en-US-short.txt")
            mock_get_charset.return_value.side_effect = Exception("Test exception")
            result = await SimpleSampleSMTPServer.handle_DATA(server, session, envelope)
            #assert SMTP server response message with Exception and status code - AC9
            assert mock_print.call_args_list == [call("Received message:"), call(f'From: {envelope.mail_from}'), call(f'To: {envelope.rcpt_tos}'), call("-----------------------"), call(f'Exception occurred while handling response:Test exception')]
            self.assertEqual(result, "250 OK")

    def test_get_charset_default_AC10(self):
        # Create a sample email envelope content
        envelope_content = b"From: sender@example.com\r\nTo: receiver@example.com\r\nSubject: Test\r\n\r\nHello, World!"
        with patch('builtins.print') as mock_print:
            mock_print.return_value = None
            # Call the get_charset method
            charset = SimpleSampleSMTPServer.get_charset(self, envelope_content)
            # Assert the expected charset value - AC10
            assert mock_print.call_args_list == [call(f'is multi-part: False'), call(f'Retrieved charset from envelope content: None')]
            self.assertEqual(charset, 'utf-8')

    def test_get_charset_AC11(self):
        # Create a sample email envelope content
        envelope_content = b"From: sender@example.com\r\nTo: receiver@example.com\r\nSubject: Test\r\n\r\nHello, World!"
        with patch('builtins.print') as mock_print:
            mock_print.return_value = None
            # Call the get_charset method
            charset = SimpleSampleSMTPServer.get_charset(self,envelope_content, default_charset='us-ascii')
            # Assert the expected charset value - AC11
            assert mock_print.call_args_list == [call(f'is multi-part: False'), call(f'Retrieved charset from envelope content: None')]
            self.assertEqual(charset, 'us-ascii')

    @pytest.mark.asyncio
    async def test_run_smtp_server_AC7(self):
        # Mock the necessary dependencies
        with patch('sample_smtp_server.socket.gethostname') as mock_gethostname, \
            patch('sample_smtp_server.socket.gethostbyname') as mock_gethostbyname, \
            patch('sample_smtp_server.SimpleSMTPRequestHandler') as mock_handler, \
            patch('sample_smtp_server.create_ssl_context') as mock_create_ssl_context, \
            patch('sample_smtp_server.Controller') as mock_controller:

            # Set up the mock return values
            mock_gethostname.return_value = 'mock_hostname'
            mock_gethostbyname.return_value = 'mock_host'
            mock_create_ssl_context.return_value = 'mock_ssl_context'

            # Run the SMTP server
            await SampleSMTPServer.run_smtp_server()

            # Assert that the necessary functions were called with the correct arguments
            mock_gethostname.assert_called_once()
            mock_gethostbyname.assert_called_once_with('mock_hostname')
            mock_handler.assert_called_once()
            mock_create_ssl_context.assert_called_once()
            mock_controller.assert_called_once_with(mock_handler.return_value, hostname='mock_host', port=9025, tls_context='mock_ssl_context')
            mock_controller.return_value.start.assert_called_once()
            #assert SMTP server listening on port - AC7
            print.assert_called_once_with("Listening for responses on mock_host:9025")

    def test_create_ssl_context(self):
        # Mock the necessary attributes and methods
        ssl_context = MagicMock()
        ssl.SSLContext = MagicMock(return_value=ssl_context)
        ssl_context.minimum_version = MagicMock()
        ssl_context.verify_mode = MagicMock()
        ssl_context.load_cert_chain = MagicMock()
        ssl_context.load_verify_locations = MagicMock()

        # Call the method under test
        result = SampleSMTPServer.create_ssl_context()

        # Assert that the necessary methods were called
        ssl.SSLContext.assert_called_once_with(protocol=ssl.PROTOCOL_TLS_SERVER)
        ssl_context.load_cert_chain.assert_called_once_with(certfile='etc/certs/listener/certificate.pem', keyfile='etc/certs/listener/private_key.pem')
        ssl_context.load_verify_locations.assert_called_once_with(cafile='etc/certs/client/certificate.pem')
        self.assertEqual(result, ssl_context)