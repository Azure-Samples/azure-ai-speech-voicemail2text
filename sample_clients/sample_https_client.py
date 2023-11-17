import ssl
import asyncio
from http import HTTPStatus
from aiohttp import ClientSession as ClientSession
from aiohttp import TCPConnector as TCPConnector
import requests
from requests import Response as Response

request_url='https://127.0.0.1:9443/transcribe'
response_url='https://v2tic.example.com:8443/response'

client_cert_path = 'etc/certs/client/certificate.pem'
client_key_path = 'etc/certs/client/private_key.pem'
server_cert_path = 'etc/certs/certificate.pem'

def create_headers():
    headers = {
        "X-Reference": "1234",
        "Connection": "close",
        "Content-Type": "audio/wav",
        "X-Return-URL": response_url,
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

def post(url, headers, data) -> Response:
    return requests.post(url, cert=(client_cert_path, client_key_path), verify=server_cert_path, data=data, headers=headers)

async def async_post(url, headers, data):
    ssl_context = create_ssl_context()
    async with ClientSession() as session:
        async with session.post(url, data=data, headers=headers, ssl_context=ssl_context) as response:
            print(f'Got [{response.status}] from {url}')
            if response.status not in [HTTPStatus.OK, HTTPStatus.ACCEPTED]:
                raise Exception
            return response

async def send_aio_https_post_request():
    audio_data = read_audio_file("etc/audio/sample-audio-en-US-short.txt")
    headers = create_headers()
    try:
        print('Sending async https request')
        response = await async_post(request_url, headers, audio_data)
        print(f'Response Status [{response.status}]')
        print(f'Response Header received SCRID Successfully [{response.headers["Location"]}]')
    except Exception as e:
        print("Exception received while sending a aio https request"+str(e))

def send_https_post_request():
    audio_data = read_audio_file("etc/audio/sample-audio-en-US-short.txt")
    headers = create_headers()
    try:
        print('Sending sync https request')
        response: Response = post(request_url, headers, audio_data)
        print(f'Response Status [{response.status_code}]')
        print(f'Response Header received SCRID Successfully [{response.headers["Location"]}]')
    except Exception as e:
        print("Exception received while sending a https request"+str(e))

if __name__ == "__main__":
    asyncio.run(send_aio_https_post_request())
    #send_https_post_request()
print("Done")