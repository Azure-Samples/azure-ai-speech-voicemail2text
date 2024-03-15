#!/usr/bin/env python
# coding: utf-8
# Copyright (c) Microsoft. All rights reserved.
# Licensed under the MIT license. See LICENSE.md file in the project root for full license information.

import os
import re
import shutil
from api_tests.core.configmap_utils import read_config_map, get_value_from_config_map
from api_tests.app.system_utils.run_command import RunCommand
from api_tests.core.reporter import reporter
from api_tests.core.assert_utils import validate

class MakeUtils(object):
    def __init__(self):
        self.rc = RunCommand()

    def build_image(self, image_name='v2tic-pytest'):
        rc_make_build_image = self.rc.run_with_output(f"make build_image image_name={image_name}")
        actual_returncode = rc_make_build_image.returncode
        validate(0, actual_returncode, 'Validate build_image response status code')
        created_image = str(rc_make_build_image.stdout.decode('utf-8')).strip().split(':')
        actual_image_name = created_image[1].strip()
        validate(image_name,actual_image_name,'Validate Image name',contains=True)
        return actual_image_name

    def start_minikube(self):
        rc_start_minikube = self.rc.run_with_output(f"make start_minikube")
        actual_returncode = rc_start_minikube.returncode
        actual_status = str(rc_start_minikube.stdout.decode('utf-8')).strip()
        validate(0, actual_returncode, 'Validate start_minikube response status code')
        validate(expected='Minikube is already running', expected2='Done! kubectl is now configured to use "minikube" cluster',
                  actual=actual_status, message='Validate Minikube status', contains=True)

    def load_image(self, created_image):
        rc_make_load_image = self.rc.run_with_output(f"make load_image image_name={created_image}")
        actual_returncode = rc_make_load_image.returncode
        actual_output = str(rc_make_load_image.stdout.decode('utf-8')).strip()
        validate(0, actual_returncode, 'Validate load_image response status code')
        validate('Image Loading...', actual_output, 'Validate Image loading')

    def check_load_image(self, created_image):
        rc_minikube_image = self.rc.run_with_output(f"minikube image list | grep {created_image}")
        actual_returncode = rc_minikube_image.returncode
        actual_output = str(rc_minikube_image.stdout.decode('utf-8')).strip()
        validate(0, actual_returncode, 'Validate check_load_image response status code')
        validate(created_image, actual_output, 'Validate Image loaded in minikube',contains=True)

    def deploy_pod(self,created_image, deployment='https'):
        std, std_err, return_code = self.rc.popen_with_output(f"make deploy_pod image_name={created_image} deployment={deployment}", '.', 10)
        actual_output = str(std)

        validate(0, return_code, 'Validate deploy_pod response status code')
        validate(expected=f'deployment.apps/{deployment}-deployment created', expected2=f'deployment.apps/{deployment}-deployment unchanged',
                 actual=actual_output, message='Validate deployment created', contains=True)


        validate(expected=f'service/{deployment}-service created', expected2=f'service/{deployment}-service unchanged',
                 actual=actual_output, message='Validate service created', contains=True)

        validate(expected=f'configmap/{deployment}-configmap-file created', expected2=f'configmap/{deployment}-configmap-file unchanged',
                 actual=actual_output, message='Validate configmap created', contains=True)

        validate('',str(std_err), 'Validate no error is encountered')
        
    def validate_configmap(self, deployment='https'):
        file_path = f'etc/deployments/{deployment}/configmap-file-instance.yaml'
        config_map_data = read_config_map(file_path)
        
        if config_map_data:
            key_to_find = 'acs_client_speech_key'
            value = get_value_from_config_map(config_map_data, key_to_find)
            
            if value is not None:
                print(f"The value for key '{key_to_find}' is: {value}")
            else:
                print(f"Key '{key_to_find}' not found in the ConfigMap.")
        else:
            print("Failed to read ConfigMap file.")

    def deploy_pod_speech_key_url_missing(self,created_image, deployment='https'):
        std, std_err, return_code = self.rc.popen_with_output(f"make deploy_pod image_name={created_image} deployment={deployment}", '.', 10)
        actual_output = str(std)

        validate(0, return_code, 'Validate deploy_pod response status code')
        validate(expected=f'{deployment}\nSPEECH_KEY was not provided, please review Makefile and ensure it\'s value is not empty',
                 actual=actual_output, message='Validate deployment failed', contains=True)
                     
    def destroy_pod(self, deployment='https'):
        rc_make_destroy_pod = self.rc.run_with_output(f"make destroy_pod deployment={deployment}", '.')
        return_code = rc_make_destroy_pod.returncode
        actual_output = str(rc_make_destroy_pod.stdout.decode('utf-8')).strip()
        validate(0, return_code, 'Validate destroy_pod response status code')
        validate(f'deployment.apps "{deployment}-deployment" deleted', actual_output, 'Validate deployment deleted', contains=True)
        validate(f'service "{deployment}-service" deleted', actual_output, 'Validate service deleted', contains=True)
        validate(f'{deployment}-configmap-file" deleted', actual_output, 'Validate configmap deleted', contains=True)

    def clean(self, deployment='https'):
        rc_make_clean = self.rc.run_with_output(f"make clean deployment={deployment}", '.')
        return_code = rc_make_clean.returncode
        actual_output = str(rc_make_clean.stdout.decode('utf-8')).strip()
        validate(0, return_code, 'Validate clean response status code')
        validate('Deleted pod-file.yaml',actual_output , 'Validate pod file deleted', contains=True)
        validate('Deleted configmap-file-instance.yaml', actual_output, 'Validate configmap file deleted', contains=True)

    def quick_start(self, deployment='https'):
        std_out, std_err, return_code = self.rc.popen_with_output(f"make quick_start deployment={deployment}", '.', 420)
        actual_output = str(std_out)

        validate(expected='Minikube is already running', expected2='Done! kubectl is now configured to use "minikube" cluster',
                  actual=actual_output, message='Validate Minikube status', contains=True)

        validate(expected=f'Image Loading...',
                 actual=actual_output, message='Validate Image loading', contains=True)
        validate(0, return_code, 'Validate deploy_pod response status code')

        validate(expected=f'deployment.apps/{deployment}-deployment created', expected2=f'deployment.apps/{deployment}-deployment unchanged',
                 actual=actual_output, message='Validate deployment created', contains=True)

        validate(expected=f'service/{deployment}-service created', expected2=f'service/{deployment}-service unchanged',
                 actual=actual_output, message='Validate service created', contains=True)

        validate(expected=f'configmap/{deployment}-configmap-file created', expected2=f'configmap/{deployment}-configmap-file unchanged',
                 actual=actual_output, message='Validate configmap created', contains=True)

        validate(expected='Please execute command python sample_clients/sample_https_client.py',
                 actual=actual_output, message='Validate static message', contains=True)

        validate(expected='Forwarding from 127.0.0.1',
                 actual=actual_output, message='Validate port forwarding', contains=True)

    def kubectl(self):
        rc_kubectl = self.rc.run_with_output(f"kubectl get all")
        
    def override_makefile(self, makefile_path, key, new_value):
        with open(makefile_path, 'r') as file:
            makefile_content = file.read()

        # Use regular expression to find and replace key-value pairs
        pattern = re.compile(fr'{re.escape(key)}\s*:=\s*.*')
        replacement = f'{key} := {new_value}'
        updated_content = re.sub(pattern, replacement, makefile_content)

        with open(makefile_path, 'w') as file:
            file.write(updated_content)
        
    def restore_makefile(self, makefile_path, backup_path):
        shutil.copy2(backup_path, makefile_path)
        os.remove(backup_path)
        
    def backup_makefile(self, makefile_path, backup_path):
        shutil.copy2(makefile_path, backup_path)
