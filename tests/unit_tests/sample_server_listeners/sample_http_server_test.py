#!/usr/bin/env python
# coding: utf-8
# Copyright (c) Microsoft. All rights reserved.
# Licensed under the MIT license. See LICENSE.md file in the project root for full license information.

from http import HTTPStatus
import unittest
from email.message import Message
from unittest.mock import MagicMock, patch, call
import ssl, sys, os
from aiohttp import ClientTimeout as ClientTimeout
from aiohttp import ClientSession as ClientSession
from aiohttp import TCPConnector as TCPConnector
sys.path.append(os.path.join(os.path.abspath(os.curdir)))
import sample_server_listeners.sample_http_server as SampleHTTPServer
from sample_server_listeners.sample_http_server import SimpleHTTPRequestHandler as SimpleSampleHTTPServer

response_url='https://v2tic.example.com:8443/response'

def read_audio_file(audio_file_path: str) -> bytes:
        with open(audio_file_path, "rb") as audio_file:
            audio_data = audio_file.read()
            return audio_data

def create_message_headers():
    message = Message()
    message.add_header('Content-Length', '10')
    message.add_header('X-Reference', '1234')
    message.add_header("Connection", "close")
    message.add_header("Content-Type", "audio/wav")
    message.add_header("X-Return-URL", response_url)
    message.add_header("Content-Encoding", "base64")
    return message

class TestSampleHTTPListener(unittest.TestCase):
    def test_do_GET_AC1(self):
        # Mock the necessary attributes and methods
        self.send_response_called = False
        self.end_headers_called = False
        self.wfile_write_called = False

        def send_response_mock(status_code):
            self.assertEqual(status_code, 200)
            self.send_response_called = True

        def end_headers_mock():
            self.end_headers_called = True

        def wfile_write_mock(content):
            self.assertEqual(content, b'Hello, GET request received!')
            self.wfile_write_called = True

        with patch('sample_server_listeners.sample_http_server.SimpleHTTPRequestHandler', new_callable=MagicMock) as mock_http_listener:
            mock_http_listener_instance = mock_http_listener.return_value
            mock_http_listener_instance.send_response = MagicMock(side_effect=send_response_mock)
            mock_http_listener_instance.end_headers = MagicMock(side_effect=end_headers_mock)
            mock_http_listener_instance.wfile.write = MagicMock(side_effect=wfile_write_mock)
            mock_http_listener_instance.path = '/'
            SimpleSampleHTTPServer.do_GET(mock_http_listener_instance)
            #AC1 - assert the GET request response body
            self.assertTrue(self.send_response_called)
            self.assertTrue(self.end_headers_called)
            self.assertTrue(self.wfile_write_called)

    def test_do_POST_AC3(self):
        with patch('sample_server_listeners.sample_http_server.SimpleHTTPRequestHandler', new_callable=MagicMock) as mock_http_listener:
            mock_http_listener_instance = mock_http_listener.return_value
            mock_http_listener_instance.print_response = MagicMock()
            SimpleSampleHTTPServer.do_POST(mock_http_listener_instance)
            #assert the POST request response body
            mock_http_listener_instance.print_response.assert_called_once()
            assert mock_http_listener_instance.print_response.call_args_list == [call()]

    def test_do_PUT_AC3(self):
        with patch('sample_server_listeners.sample_http_server.SimpleHTTPRequestHandler', new_callable=MagicMock) as mock_http_listener:
            mock_http_listener_instance = mock_http_listener.return_value
            mock_http_listener_instance.print_response = MagicMock()
            SimpleSampleHTTPServer.do_PUT(mock_http_listener_instance)
            #assert the PUT request response body
            mock_http_listener_instance.print_response.assert_called_once()
            assert mock_http_listener_instance.print_response.call_args_list == [call()]

    def test_print_response_default_charset_AC3_AC5(self):
        audio_data = read_audio_file("etc/audio/sample-audio-en-US-short.txt")

        with patch('sample_server_listeners.sample_http_server.SimpleHTTPRequestHandler', new_callable=MagicMock) as mock_http_listener, \
             patch('builtins.print') as mock_print:
            mock_http_listener_instance = mock_http_listener.return_value
            mock_http_listener_instance.headers = create_message_headers()
            mock_http_listener_instance.print_response_headers = MagicMock()
            # mock_http_listener_instance.headers.get_content_charset.return_value = 'utf-8'
            mock_http_listener_instance.path = '/response'
            mock_http_listener_instance.rfile.read.return_value = audio_data
            mock_http_listener_instance.send_response = MagicMock()
            SimpleSampleHTTPServer.print_response(mock_http_listener_instance)
            #AC3 AC5 - assert headers, body and status code of the response with default charset
            #verify the headers of the response will be called
            mock_http_listener_instance.print_response_headers.assert_called_once()
            assert mock_http_listener_instance.print_response_headers.call_args_list == [call()]
            #verify the print statements for body of the response
            assert mock_print.call_args_list == [call("-----------------------"), call("Received Response:"), call(f'Message Content:{os.linesep}{audio_data.decode()}')]
            #verify HTTPS response status code as 200 (HTTPStatus.OK)
            assert mock_http_listener_instance.send_response.call_args_list == [call(HTTPStatus.OK)]

    def test_print_response_charset_defined_AC3_AC6(self):
        audio_data = read_audio_file("etc/audio/sample-audio-en-US-short.txt")

        with patch('sample_server_listeners.sample_http_server.SimpleHTTPRequestHandler', new_callable=MagicMock) as mock_http_listener, \
             patch('builtins.print') as mock_print:
            mock_http_listener_instance = mock_http_listener.return_value
            message = create_message_headers()
            message.replace_header('Content-Type', 'audio/wav; charset=us-ascii')
            mock_http_listener_instance.headers = message
            mock_http_listener_instance.print_response_headers = MagicMock()
            # mock_http_listener_instance.headers.get_content_charset.return_value = 'us-ascii'
            mock_http_listener_instance.path = '/response'
            mock_http_listener_instance.rfile.read.return_value = audio_data
            mock_http_listener_instance.send_response = MagicMock()
            SimpleSampleHTTPServer.print_response(mock_http_listener_instance)
            #AC3 AC6 - assert headers, body and status code of the response with charset defined
            #verify the headers of the response will be called
            mock_http_listener_instance.print_response_headers.assert_called_once()
            assert mock_http_listener_instance.print_response_headers.call_args_list == [call()]
            #verify the print statements for body of the response
            assert mock_print.call_args_list == [call("-----------------------"), call("Received Response:"), call(f'Message Content:{os.linesep}{audio_data.decode()}')]
            #verify HTTPS response status code as 200 (HTTPStatus.OK)
            assert mock_http_listener_instance.send_response.call_args_list == [call(HTTPStatus.OK)]

    def test_print_response_exception_caught_AC4(self):
        audio_data = read_audio_file("etc/audio/sample-audio-en-US-short.txt")

        with patch('sample_server_listeners.sample_http_server.SimpleHTTPRequestHandler', new_callable=MagicMock) as mock_http_listener, \
             patch('builtins.print') as mock_print:
            mock_http_listener_instance = mock_http_listener.return_value
            mock_http_listener_instance.headers = create_message_headers()
            mock_http_listener_instance.path = '/response'
            mock_http_listener_instance.rfile.read.return_value = audio_data
            mock_http_listener_instance.send_response = MagicMock()
            mock_http_listener_instance.print_response_headers.side_effect = Exception('Custom Exception Message')
            SimpleSampleHTTPServer.print_response(mock_http_listener_instance)
            #AC4 - assert headers, exception and status code of the response
            #verify the headers of the response will be called
            mock_http_listener_instance.print_response_headers.assert_called_once()
            assert mock_http_listener_instance.print_response_headers.call_args_list == [call()]
            #verify the print statements for body of the response with Exception Message
            assert mock_print.call_args_list == [call("-----------------------"), call("Received Response:") , call('Exception occurred while handling response:Custom Exception Message')]
            #verify HTTPS response status code as 200 (HTTPStatus.OK)
            assert mock_http_listener_instance.send_response.call_args_list == [call(HTTPStatus.OK)]


    def test_print_response_headers_AC3(self):
         with patch('sample_server_listeners.sample_http_server.SimpleHTTPRequestHandler', new_callable=MagicMock) as mock_http_listener, \
              patch('builtins.print') as mock_print:
                mock_http_listener_instance = mock_http_listener.return_value
                mock_http_listener_instance.headers = create_message_headers()
                #AC3 - assert print headers of the response
                SimpleSampleHTTPServer.print_response_headers(mock_http_listener_instance)
                assert mock_print.call_args_list == [call('Content-Length: 10'), call('X-Reference: 1234'), call('Connection: close'), call('Content-Type: audio/wav'), call('X-Return-URL: https://v2tic.example.com:8443/response'), call('Content-Encoding: base64')]

class TestSampleHTTPServer(unittest.TestCase):
    @patch('socket.gethostname', return_value='mocked_hostname')
    @patch('socket.gethostbyname', return_value='mocked_host')
    def test_run_http_AC2(self, mock_gethostbyname, mock_gethostname):
        with patch('sample_server_listeners.sample_http_server.create_ssl_context', new_callable=MagicMock) as mock_create_ssl_context, \
             patch('builtins.print', new_callable=MagicMock) as mock_print, \
             patch('sample_server_listeners.sample_http_server.HTTPServer' , new_callable=MagicMock) as mock_http_server:
                mock_ssl_context = MagicMock()
                mock_create_ssl_context.return_value = mock_ssl_context

                # Mock HTTPServer instance
                mock_http_server_instance = mock_http_server.return_value
                mock_socket = MagicMock()
                mock_http_server_instance.socket = mock_socket

                # Call your method
                SampleHTTPServer.run_http()

                # Assertions
                mock_gethostname.assert_called_once()
                mock_gethostbyname.assert_called_once_with('mocked_hostname')
                mock_create_ssl_context.assert_called_once()
                mock_ssl_context.wrap_socket.assert_called_once_with(mock_socket, server_side=True)
                #AC2 - assert the HTTP server is listening on port 8443 and print the message
                mock_http_server.assert_called_once_with(('mocked_host', 8443), SimpleSampleHTTPServer)
                #mock_print.assert_called_once_with('HTTPS Server listening for responses on https://mocked_host:8443/response')
                mock_http_server_instance.serve_forever.assert_called_once()

    def test_create_ssl_context(self):
        # Mock the necessary attributes and methods
        ssl_context = MagicMock()
        ssl.SSLContext = MagicMock(return_value=ssl_context)
        ssl_context.minimum_version = MagicMock()
        ssl_context.verify_mode = MagicMock()
        ssl_context.load_cert_chain = MagicMock()
        ssl_context.load_verify_locations = MagicMock()

        # Call the method under test
        result = SampleHTTPServer.create_ssl_context()

        # Assert that the necessary methods were called
        ssl.SSLContext.assert_called_once_with(protocol=ssl.PROTOCOL_TLS_SERVER)
        ssl_context.load_cert_chain.assert_called_once_with(certfile='etc/certs/listener/certificate.pem', keyfile='etc/certs/listener/private_key.pem')
        ssl_context.load_verify_locations.assert_called_once_with(cafile='etc/certs/client/certificate.pem')
        self.assertEqual(result, ssl_context)