#!/usr/bin/env python
# coding: utf-8
# Copyright (c) Microsoft. All rights reserved.
# Licensed under the MIT license. See LICENSE.md file in the project root for full license information.

import docker
import time
import subprocess
import api_tests.core.server_status_utils as server_status_utils
from api_tests.core.reporter import reporter


RUNNING = 'running'

def get_docker_client():
    return docker.from_env()
#Global variables

def is_running(container_name):
    """
    verify the status of a sniffer container by it's name
    :param container_name: the name of the container
    :return: Boolean if the status is ok
    """
    client = get_docker_client()
    try:
        container = client.containers.get(container_name)
        container_state = container.attrs['State']
        container_is_running = container_state['Status'] == RUNNING
        return container_is_running
    except docker.errors.NotFound:
        return False

def delete_images(image_name_prefix: str):
    client = get_docker_client()
    images = client.images.list()

    images_to_delete = [image for image in images if any(tag.startswith(image_name_prefix) for tag in image.tags)]

    for image in images_to_delete:
        try:
            image.remove(force=True)
            reporter.report(f"Image {image.tags[0]} was deleted")
        except Exception as e:
            reporter.report(f"Image {image.tags[0]} was not deleted due to {e}")

def delete_container_and_image(container_name: str):
    client = get_docker_client()
    try:
        container = client.containers.get(container_name)
        container_image = container.image.tags
    except docker.errors.NotFound:
        reporter.report(f"Container {container_name} was not found")
        return

    try:
        container.remove(force=True)
        reporter.report(f"Container {container_name} was deleted")
    except Exception as e:
        reporter.report(f"Container {container_name} was not deleted due to {e}")

    delete_images(container_image[0])


def check_pod_server_status(host: str, port: int, timeout: int):
    """
    Check the status of the pod server
    :param host: the host of the pod server
    :param port: the port of the pod server
    :param timeout: the timeout in seconds
    :return: Boolean if the pod server is running
    """
    try:
        pod_server_port_running = server_status_utils.query_server_status(True, "POD Server", host, port, timeout)
    except TimeoutError:
        pod_server_port_running = False
    return pod_server_port_running


def wait_till_docker_container_start(container_name: str, timeout: int, host: str,port: int):
    """
    Wait till a docker container is up and running
    :param container_name: the name of the container
    :param timeout: the timeout in seconds
    :return: Boolean if the container is running
    """
    start = time.time()
    container_running = False
    http_test_pod_port_running = False

    while True:
        reporter.report(f"Waiting for docker conatiner with name {container_name} to start and its current status is {is_running(container_name)}")
        elapsed = time.time() - start

        if elapsed > timeout:
            raise TimeoutError("The condition is not true after {} seconds".format(timeout))

        if is_running(container_name):
            reporter.report(f"Container {container_name} is running")
            container_running = True
            break

        time.sleep(20)

    # Wait for the pod server to be up and running
    http_test_pod_port_running = server_status_utils.query_server_status(True, "POD Server", host, port, timeout-elapsed)
    if http_test_pod_port_running:
        reporter.report(f"POD Server is running on port {port}")

    return container_running and http_test_pod_port_running