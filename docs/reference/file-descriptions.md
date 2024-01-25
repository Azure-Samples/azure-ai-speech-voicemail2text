# File descriptions

This is a glossary of the files you'll find and use within the V2TIC repository. To see how these components interact, go to [Architecture](../about/architecture.md).

## AcsClient

`AcsClient` processes and sends transcription requests to Azure AI, then receives and processes transcription responses.

## Common folder

The `Common` folder contains the Python scripts that setup classes, dictionaries, definitions, and more. These handle and process incoming HTTPS and SMTP protocols until the end of delivery of the transcription response.

## etc folder

The `etc` folder contains these folders:
    - `audio` contains sample audio for testing.
    - `certs` with certification keys.
    - `config` with the `config.properties` file. This file contains the global configuration settings specified as key-value pairs for service protocols, as well as ACS specification. Properties set in `configmap-file.yaml` override properties set in `config.properties`. Go to [Configuration fields](../reference/deploy-configurations-templates.md) for more information.
    - `deployments` with .yaml configuration and deployment files for HTTPS and SMTP service protocols:
        - `configmap-file.yaml`: a configuration file for a Kubernetes resource to store configuration data for service deployments that can be referenced by pods/deployments.
        - `deployment-file.yaml`: a configuration file for service deployments that defines the container resources and references the configuration data of service deployments in `configmap-file.yaml`.
    - `profiles`, which contains a set of sample profile, and templates for both HTTPS and SMTP deployments.
        - `request.j2`: a Jinja template that defines the key-value pairs of the request.
        - `response.j2`: a Jinja template that defines the key-value pairs of the response.
        - `profile.py`: a Python script that maps the key-value pairs of the request and response templates.

## sample_server_listeners folder

This folder contains sample Python programs that can capture final responses during testing for HTTPS and SMTP deployments. Go to [Test and validate](../test-validate/test-validate.md) for more information.

## sample_clients folder

This folder contains sample apps for HTTPS and SMTP deployments. Go to [Build and deploy](../build-deploy/build-summary.md) to learn how to run the sample apps.

## servers folder

The `servers` folder contains both an HTTPS and SMTP server engines to process and handle each type of request.

## v2ticlib folder

The `v2ticlib` folder contains V2TIC-supported utility Python scripts. You should not need to configure these files.

## Other files

- `Makefile`: a text file to automate build and execution tasks such as building Docker image(s), loading image(s) to minikube, deploying image(s) and running services on pods. Some configuration in `Makefile` is required to build an image. Go to [Required configuration](../reference/configure-makefile.md) for more information.
- `Dockerfile`: outlines the steps to create the Docker image that includes Ubuntu version 20.04, Python 3.9, and all necessary requirements.
- `Requirements.txt`: a list of Python dependencies required to build a Docker image. These are part of the [prerequistes](../about/prerequisites.md) for building and deploying V2TIC.

[Return to table of contents](../index.md)