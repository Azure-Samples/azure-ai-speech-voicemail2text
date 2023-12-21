#!/usr/bin/env python
# coding: utf-8
# Copyright (c) Microsoft. All rights reserved.
# Licensed under the MIT license. See LICENSE.md file in the project root for full license information.



from Common.Ejector.abstract_ejector import Ejector
from Common.Ejector.http_ejector import HttpEjector
from Common.Ejector.smtp_ejector import SmtpEjector
from v2ticlib.constants.protocols import HTTPS, SMTP
import v2ticlib.request_utils as request_utils
import v2ticlib.config_utils as config_utils
import v2ticlib.constants.constants as CONSTANTS

ejectors = {}
ejectors[HTTPS] = HttpEjector()
ejectors[SMTP] = SmtpEjector()

async def eject(request, response):
    delivery_type = request_utils.get_delivery_type(request)
    ejector: Ejector = ejectors[delivery_type]
    await ejector.eject(request, response)