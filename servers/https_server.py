#!/usr/bin/env python
# coding: utf-8
# Copyright (c) Microsoft. All rights reserved.
# Licensed under the MIT license. See LICENSE.md file in the project root for full license information.



import asyncio
import sys, os, typing, traceback
from aiohttp import web
from aiohttp.web import Request
from aiohttp.web import middleware
from aiohttp.web_runner import GracefulExit
from http import HTTPStatus

sys.path.append(os.path.join(os.path.abspath(os.curdir)))
from v2ticlib.logger_utils import log, CONTEXT
from Common.request_injestor import RequestInjestor
import Common.request_handler as request_handler
from v2ticlib import config_utils
from v2ticlib.constants.protocols import HTTPS
from v2ticlib.constants.fields import SCRID, DELIVERY_TYPE
from v2ticlib.constants.headers import LOCATION
import v2ticlib.coroutine_timeout_utils as coroutine_timeout
import v2ticlib.request_utils as request_utils
import v2ticlib.ssl_context_utils as ssl_context_utils

routes = web.RouteTableDef()
injestor = RequestInjestor()
consume_request_timeout = config_utils.get_consume_request_timeout()
app = None
global keep_server_alive
keep_server_alive:bool = True

@routes.get("/")
async def index():
    return {"message":"Welcome to V2TIC interface"}

@middleware
async def filter_middleware(request: Request, handler):

    # skipp process stub
    if request.path == '/response':
        return await handler(request)

    try:
        initial_request_content:dict = request_utils.generate_initial_request_content()
        initial_request_content[DELIVERY_TYPE] = HTTPS
        CONTEXT.set(initial_request_content[SCRID])
        return await coroutine_timeout.timeout_after(handler(initial_request_content, request), timeout=consume_request_timeout)
    except Exception as e:
        stack = traceback.format_exc()
        log(f'Timed out processing request: {e} - {stack}')
        return web.Response(status=HTTPStatus.GATEWAY_TIMEOUT, text=str(e))

@routes.post("/transcribe")
@routes.put("/transcribe")
async def handler(initial_request_content:dict, external_request: Request):
    log(f'Received request')
    headers: typing.Mapping[str, str] = external_request.headers
    body: bytes = await external_request.read()
    try:
        handle_request(initial_request_content, headers, body)
    except Exception as e:
        stack = traceback.format_exc()
        log(f'Error processing request: {e} - {stack}')
        return web.Response(status=HTTPStatus.BAD_REQUEST, text=str(e))

    headers = {}
    headers[LOCATION] = initial_request_content[SCRID]
    return web.Response(status=HTTPStatus.ACCEPTED, headers=headers)

def handle_request(initial_request_content:dict, headers: typing.Mapping[str, str], body: bytes):
    request = injestor.injest(initial_request_content, headers, body)
    asyncio.create_task(process_request(request))

async def process_request(request):
    scrid = request_utils.get_scrid(request)
    CONTEXT.set(scrid)
    await request_handler.process_request(request)

# Stub Response
@routes.post("/response")
async def stub_response(request: Request):
    print(f'Stub handled response:')
    response = await request.read()
    for key,val in request.headers.items():
        print(f'{key}: {val}')
    print(f'Body: {response.decode()}')
    return web.Response(status=HTTPStatus.OK)

async def start_https_server():
    host = config_utils.get_host()
    port = config_utils.get_port()
    ssl_context = ssl_context_utils.create_server_ssl_context()
    app = web.Application(middlewares=[filter_middleware], client_max_size=1024**3)
    app.add_routes(routes)
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, host=host, port=port, ssl_context=ssl_context)
    await site.start()
    print(f'HTTPS Server Listening On: {host}:{port}')

    global keep_server_alive
    while keep_server_alive:
        await asyncio.sleep(1)

def stop_server():
    global keep_server_alive
    keep_server_alive = False

if __name__ == "__main__":
    asyncio.run(start_https_server())
