#!/usr/bin/env python
# coding: utf-8
# Copyright (c) Microsoft. All rights reserved.
# Licensed under the MIT license. See LICENSE.md file in the project root for full license information.



from Common.Ejector.abstract_ejector import Ejector
import v2ticlib.http_client_utils as http_util
import v2ticlib.constants.fields as Fields
from v2ticlib.retry_utils import retry_with_custom_strategy
from v2ticlib.logger_utils import log
import v2ticlib.constants.constants as Constants

class HttpEjector(Ejector):
    async def eject(self, request:dict, response:dict) -> str:
        url = response[Fields.RETURN_URL]
        headers = response[Fields.HEADERS]
        content = response[Fields.BODY]
        try:
            return await self.do_eject(url, headers, content)
        except Exception as e:
            log(self.do_eject.retry.statistics)
            raise e

    @retry_with_custom_strategy(Constants.EJECTOR)
    async def do_eject(self, url, headers, content) -> str:
        timeout = self.get_timeout()
        return await http_util.post(url, headers, content, timeout)
