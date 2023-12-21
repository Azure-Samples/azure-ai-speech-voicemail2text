#!/usr/bin/env python
# coding: utf-8
# Copyright (c) Microsoft. All rights reserved.
# Licensed under the MIT license. See LICENSE.md file in the project root for full license information.



from typing import Final
from aiohttp import ClientTimeout as ClientTimeout
from aiohttp import ClientSession as ClientSession
from aiohttp import TCPConnector as TCPConnector
from v2ticlib.logger_utils import log
from http import HTTPStatus
import v2ticlib.ssl_context_utils as ssl_context_utils

async def post(url, headers, data, timeout) -> str:
    ssl_context = ssl_context_utils.create_client_ssl_context()
    async with ClientSession() as session:
        async with session.post(url, data=data, headers=headers, ssl_context=ssl_context, timeout=timeout) as response:
            log(f'Got [{response.status}] from {url}')
            if response.status not in [HTTPStatus.OK, HTTPStatus.ACCEPTED]:
                # TODO make exception pristine!
                raise Exception
            return_code = f'{response.status}'
            return return_code