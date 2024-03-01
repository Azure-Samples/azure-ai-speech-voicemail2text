#!/usr/bin/env python
# coding: utf-8
# Copyright (c) Microsoft. All rights reserved.
# Licensed under the MIT license. See LICENSE.md file in the project root for full license information.



import pytest
import os
import sys
import pytest
sys.path.append(os.path.join(os.path.abspath(os.curdir)))
from api_tests.app.system_utils.make_utils import MakeUtils

@pytest.mark.makecommands
@pytest.mark.makecommandsmtp
#@pytest.mark.makeregression
def test_make_commands():
    #created_image = 'v2tic-pytest_20231018-173705'
    image_name = 'v2tic-pytest'
    make_utils = MakeUtils()
    created_image = make_utils.build_image(image_name)
    make_utils.start_minikube()
    make_utils.load_image(created_image)
    make_utils.check_load_image(created_image)
    make_utils.deploy_pod(created_image,deployment='smtp')
    make_utils.destroy_pod(deployment='smtp')
    make_utils.clean(deployment='smtp')
    
@pytest.mark.makecommandsmtpspeechkeyurlmissing
def test_make_commands_AC1():
    #test case when speech key and endpoint url are missing
    image_name = 'v2tic-pytest'
    make_utils = MakeUtils()
    make_utils.backup_makefile('Makefile', 'Makefile.backup')
    make_utils.override_makefile('Makefile', 'SPEECH_KEY', '')
    make_utils.override_makefile('Makefile', 'END_POINT', '')
    created_image = make_utils.build_image(image_name)
    make_utils.start_minikube()
    make_utils.load_image(created_image)
    make_utils.check_load_image(created_image)
    make_utils.deploy_pod_speech_key_url_missing(created_image,deployment='smtp')
    make_utils.restore_makefile('Makefile', 'Makefile.backup')
    
@pytest.mark.makecommandsmtpspeechkeyurl
def test_make_commands_AC5():
    #test case when speech key and endpoint url are correct
    image_name = 'v2tic-pytest'
    make_utils = MakeUtils()
    created_image = make_utils.build_image(image_name)
    make_utils.start_minikube()
    make_utils.load_image(created_image)
    make_utils.check_load_image(created_image)
    make_utils.deploy_pod(created_image,deployment='smtp')
    make_utils.validate_configmap(deployment='smtp')
    #once validated the config map instance file, we can now remove this configmap
    make_utils.destroy_pod(deployment='smtp')
    make_utils.clean(deployment='smtp')
