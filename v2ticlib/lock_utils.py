#!/usr/bin/env python
# coding: utf-8
# Copyright (c) Microsoft. All rights reserved.
# Licensed under the MIT license. See LICENSE.md file in the project root for full license information.


import threading
from contextlib import contextmanager
import v2ticlib.config_utils as config_utils

global lock_dict
lock_dict = {}

def _get_lock(key):
  lock = lock_dict.get(key)
  if lock is None:
    lock = threading.RLock()
    lock_dict[key] = lock
  return lock

@contextmanager
def get_lock_with_timeout(key):
  lock = _get_lock(key)
  result = lock.acquire(timeout=config_utils.get_locking_default_timeout())
  try:
    yield result
  finally:
     if result:
       lock.release()
