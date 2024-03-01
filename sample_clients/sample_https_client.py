#!/usr/bin/env python
# coding: utf-8
# Copyright (c) Microsoft. All rights reserved.
# Licensed under the MIT license. See LICENSE.md file in the project root for full license information.


import argparse
import ssl
import asyncio
from http import HTTPStatus
from aiohttp import ClientSession as ClientSession
from aiohttp import TCPConnector as TCPConnector
from requests import Response as Response

client_cert_path = 'etc/certs/client/certificate.pem'
client_key_path = 'etc/certs/client/private_key.pem'
server_cert_path = 'etc/certs/certificate.pem'

def create_request_url(host, port):
    return f'https://{host}:{port}/transcribe'

def create_headers(response_host, response_port):
    headers = {
        "X-Reference": "1234",
        "Connection": "close",
        "Content-Type": "audio/wav",
        "X-Return-URL": f'https://{response_host}:{response_port}/response',
        "Content-Encoding": "base64"
    }
    return headers

def read_audio_file(audio_file_path: str) -> bytes:
    with open(audio_file_path, "rb") as audio_file:
        audio_data = audio_file.read()
        return audio_data

def create_ssl_context():
    ssl_context = ssl.SSLContext(protocol=ssl.PROTOCOL_TLS_CLIENT)
    ssl_context.minimum_version = ssl.TLSVersion.TLSv1_2
    ssl_context.load_cert_chain(certfile=client_cert_path, keyfile=client_key_path)
    ssl_context.load_verify_locations(cafile=server_cert_path)
    return ssl_context

async def async_post(url, headers, data):
    ssl_context = create_ssl_context()
    async with ClientSession() as session:
        async with session.post(url, data=data, headers=headers, ssl_context=ssl_context) as response:
            print(f'Got [{response.status}] from {url}:')
            print(f'{await response.text()}')

            if response.status not in [HTTPStatus.OK, HTTPStatus.ACCEPTED]:
                raise Exception
            return response

async def send_aio_https_post_request(host, port, response_host, response_port):
    audio_data = read_audio_file("etc/audio/sample-audio-en-US-short.txt")
    request_url = create_request_url(host, port)
    headers = create_headers(response_host, response_port)
    try:
        print('Sending async https request')
        response = await async_post(request_url, headers, audio_data)
        print(f'Response Status [{response.status}]')
        print(f'Response Header received SCRID Successfully [{response.headers["Location"]}]')
        return response
    except Exception as e:
        print("Exception received while sending a aio https request"+str(e))

if __name__ == "__main__":

    argParser = argparse.ArgumentParser()
    argParser.add_argument("--host", type=str, help="hostname", default="https-server.v2tic.com", required=False)
    argParser.add_argument("--port", type=int, help="port", default=9443, required=False)
    argParser.add_argument("--response_host", type=str, help="response hostname", default="https-listener.v2tic.com", required=False)
    argParser.add_argument("--response_port", type=int, help="response port", default=8443, required=False)

    args = argParser.parse_args()
    print("args=%s" % args)

    asyncio.run(send_aio_https_post_request(args.host, args.port, args.response_host, args.response_port))
print("Done")