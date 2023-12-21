#!/usr/bin/env python
# coding: utf-8
# Copyright (c) Microsoft. All rights reserved.
# Licensed under the MIT license. See LICENSE.md file in the project root for full license information.



from threading import current_thread
from datetime import datetime
from v2ticlib import config_utils
import contextvars

global CONTEXT
CONTEXT = contextvars.ContextVar("SCRID", default='Unknown_Scrid')

def log(*args, **kwargs):
    id = CONTEXT.get()
    thread_id = current_thread().getName()
    print(f'[{datetime.now()}][{thread_id}][{id}]',flush=True, *args, **kwargs)

def debug(*args, **kwargs):
    if is_logging_level_debug():
        log(*args, **kwargs)

def is_logging_level_debug():
    return config_utils.get_logging_level() == 'debug'
