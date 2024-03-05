# Azure AI Speech Voicemail to Text Solution Accelerator

Welcome to the Azure AI Speech Voicemail to Text Solution Accelerator repository! The Azure AI Speech Voicemail to Text Solution Accelerator is a powerful tool that lets you convert voicemails directly to text using speech detection AI!

## About this repo
This repository provides a template for setting up the solution accelerator, along with detailed instructions on how to use and customize it to your specific needs.

## Overview
This README file documents the process to create a Voicemail to Text Integration Client (V2TIC) project by building a Docker image, deploying it to Minikube, and exposing it as a service.

## Documentation
This Readme is designed as a quickstart guide to get you started with the Accelerator quickly. To find more in-depth concepts, visit the [index of documents](/docs/index.md) to help you navigate our documentation more easily.

## Prerequisites
Option 1:  **_Server-side_**
  - [Docker](https://docs.docker.com/get-docker/)
  - [Minikube](https://minikube.sigs.k8s.io/docs/start/)
  - [kubectl](https://kubernetes.io/docs/tasks/tools/)
  - Make/Shell/envsubst (available by default on most Ubuntu systems). For Windows, refer to the [additional resources](#additional-resources) section.

Option 2: **_Client-side_**

- [Python 3.9](https://www.python.org/downloads/release/python-390/) (To run sample_server_listeners)
- [Pip](https://pypi.org/project/pip/)
  - Open Command Prompt/terminal.
  - Navigate to the location of your **azure-ai-speech-voicemail2text** folder.
  - Run command **pip install -r requirements.txt**.

## Usage

Clone and checkout the repository.

```bash
git clone https://github.com/Azure-Samples/azure-ai-speech-voicemail2text.git

cd azure-ai-speech-voicemail2text

```

Open the project in [Visual Studio Code](https://code.visualstudio.com/download) or any other editor.

> [!IMPORTANT]
> In the Makefile in the root folder, you **must** populate the list of tuple `SPEECH_RESOURCES` values with your speech key and endpoint URL.
> The maximum number of tuples in SPEECH_RESOURCES is 2.
>
> **Examples**: 
1. 1 pair of speech key and endpoint. Region failover is not enabled
 `SPEECH_RESOURCES := [('******************************8b','wss://westus.stt.speech.microsoft.com/speech/universal/v2')]`
2. 2 pairs of speech key and endpoint. Region failover is enabled
`SPEECH_RESOURCES := [('******************************8b','wss://westus.stt.speech.microsoft.com/speech/universal/v2'), ('******************************fe','wss://eastus.stt.speech.microsoft.com/speech/universal/v2')]`


**Optional**: If needed, modify the _configmap-file.yaml_ file to override configuration values under etc/deployments.

## Getting Started

- In the scenarios outlined below, Ubuntu 20.04 was used in Linux testing.
- Depending on your installation, the commands below may require sudo.
- Depending on your installation package of python, you may need to input python3.9 instead of python.

Run these commands to build, load and deploy a docker image. All commands must be run in a Git Bash terminal

1. Run `cd <path_to_project_parent_folder>` where code is checked out.
```bash
cd <path_to_project_parent_folder>
```

2. Run `make start_minikube` to start Minikube. If it is already running, the status will be displayed. Else, the command will start the cluster. If you need to ensure a fresh minikube container is created, run `minikube delete` followed by `minikube start` before this command.
```bash
make start_minikube
```

3. Run `make build_image` to build the Docker image. Provide a value for `<image_name>`, else it will default to `default_image_datetimestamp`. `<image_name>` must be lowercase.
```bash
make build_image image_name=<image-name>
```
Make a note of the new `<image-name>`, displayed on screen once the image is created, as a timestamp will always be appended to `<image-name>`.

4. Run `make load_image` to load the Docker image into Minikube.
```bash
make load_image image_name=<customized-image-name>
```

5. Run `make deploy_pod` to deploy and expose the service on Kubernetes. Sample deployment values: `https`, `smtp`.
> [!IMPORTANT]
> Ensure that the folder name is the same as the deployment name and that the _configmap-file_ and _deployment-file_ yaml files are present in that folder.
```bash
make deploy_pod deployment=<name-of-deployment> image_name=<customized-image-name>
```

6. Run sanity checks on created pod.

> [!IMPORTANT]
> You **must** have executed steps as part of Prerequisites -> Option 2: **_Client-side_**. This step must also be performed in a new Git Bash terminal

Make a note of `<pod_ip>` and `<node_port>` displayed on screen after execution of make deploy_pod or make quick_start.

a) Start the sample https/smtp listener.
```bash
python sample_server_listeners/sample_http_server.py
```
or
```bash
python sample_server_listeners/sample_smtp_server.py
```
Make a note of `<ip_address>` on which listener started listening.

b) Add the noted listener `<ip_address>` as an entry for http or smtp listener server in /etc/hosts file. (for Windows, navigate to C:\Windows\System32\drivers\etc\hosts)

```bash
<ip_address> https-listener.v2tic.com smtp-listener.v2tic.com
```

c) Add the `<pod_ip>` address as an entry for http or smtp pod server in /etc/hosts file. (for Windows, navigate to C:\Windows\System32\drivers\etc\hosts)

```bash
<pod_ip> https-server.v2tic.com smtp-server.v2tic.com
```

d) Open another terminal and run sample client to send a http or smtp request to the `<pod_ip>` address and `<node_port>`

```bash
python sample_clients/sample_https_client.py --port <node_port>
```
or
```bash
python sample_clients/sample_smtp_client.py --port <node_port>
```

e) Check sample client console output for request successfully sent.

f) Check sample listener console output for request successfully transcribed and received.

### Optional steps
Run `make start_dashboard` to open the Kubernetes dashboard.
```bash
make start_dashboard
```

To delete the pod, run `make destroy` to destroy the deployment, service and configMap for the deployment you select. Sample deployment values: `https`, `smtp`.
```bash
make destroy_pod deployment=<name-of-deployment>
```

To clean up artifacts created by `make deploy_pod`, run the "make clean" command to delete the _pod-file.yaml_ file and _configmap-file-instance.yaml_ file.
```bash
make clean deployment=<name-of-deployment>
```

To enable autoscaling, run `make enable_autoscale` to enable metrics server and autoscaling on the deployment. Sample deployment values: `https`, `smtp`.
```bash
make enable_autoscale deployment=<name-of-deployment>
```

To delete autoscaling, run `make destroy_autoscale` to destroy autoscaling on the deployment. Sample deployment values: `https`, `smtp`.
```bash
make destroy_autoscale deployment=<name-of-deployment>
```

To check and display logs, run `make display_pod_logs` to display logs from the latest deployed pod. `pod_name` is displayed on console logs once deployment is successful.
```bash
make display_pod_logs pod_name=<name-of-pod>
```

Run `make quick_start` to run the end-to-end deployment: building the image from current codebase, starting minikube if it's not already running, loading the image into the minikube cluster and deploying the https or smtp image.
```bash
make quick_start deployment=<name-of-deployment>
```

## Additional Resources
• [Docker documentation](https://docs.docker.com/)

• [Minikube documentation](https://minikube.sigs.k8s.io/docs/)

• kubectl documentation: [Commands](https://kubernetes.io/docs/reference/generated/kubectl/kubectl-commands) and [tools](https://kubernetes.io/docs/tasks/tools/)

• Make: Available on [Sourceforge](https://gnuwin32.sourceforge.net/packages/make.htm) or [GNU.org](https://www.gnu.org/software/make/)

• [WSL](https://docs.microsoft.com/en-us/windows/wsl/install)

• [Cygwin](https://www.cygwin.com/)

• [Git](https://git-scm.com/downloads)

## Performance Benchmark

Benchmark tests were executed in Azure VM running HTTPS and SMTP servers at a time, using a in-house load test injection tool.

| Protocol        | VM Size | \# Pod | Test Config                    | LID_MODE            | MPM | Metrics             | RTF         | Converted | Unconverted |
| --------------- | ------- | ------ | ------------------------------ | ------------------- | --- | ------------------- | ----------- | --------- | ----------- |
| HTTPS           | D4asV5  | 1      | 1 replica , single speech key  | AtStartHighAccuracy | 240 | CPU ~32%, Mem ~19%  | 0.63        | 99.99%    | 0.01%       |
| SMTP (starttls) | D4asV5  | 1      | 1 replica , single speech key  | AtStartHighAccuracy | 240 | CPU ~42%, Mem ~15%  | 0.63        | 99.99%    | 0.01%       |
| HTTPS           | D4asV5  | 2      | 2 replicas , single speech key | AtStartHighAccuracy | 360 | CPU ~50% , Mem ~19% | 0.61 , 0.64 | 99.96%    | 0.03%       |
| SMTP (starttls) | D4asV5  | 2      | 2 replicas , single speech key | AtStartHighAccuracy | 360 | CPU ~55% , Mem ~20% | 0.42 , 0.42 | 99.99%    | 0.01%       |
| HTTPS           | D4asV5  | 2      | 1 replica , two speech keys    | AtStartHighAccuracy | 360 | CPU ~57% , Mem ~20% | 0.65 , 0.65 | 99.98%    | 0.01%       |
| SMTP (starttls) | D4asV5  | 2      | 1 replica , two speech keys    | AtStartHighAccuracy | 360 | CPU ~61% , Mem ~20% | 0.64 , 0.64 | 99.98%    | 0.02%       |

## Running V2TIC Regression tests on a local machine
### Pre-requisites
  - [Python 3.9](https://www.python.org/downloads/release/python-390/)
  - [Git Client](https://git-scm.com/downloads)
  - Setup [ffmpeg](https://github.com/BtbN/FFmpeg-Builds/releases/download/latest/ffmpeg-master-latest-win64-gpl.zip) (this link will begin the download immediately) on Windows machines.

    > [!NOTE]
    > This setup is only needed when you need to run a local server
    1. Download the latest ffmpeg
    2. Unzip the downloaded file to your C: drive
    3. Rename the extracted folder to ffmpeg
    4. Set the environment path variable for ffmpeg by running the following command: `setx /m PATH "C:\ffmpeg\bin;%PATH%"`
    5. Restart terminal/command prompt
    6. Verify the installation by running: ffmpeg –version

### Checkout the branch and install required packages
```bash
git clone https://github.com/Azure-Samples/azure-ai-speech-voicemail2text.git
cd azure-ai-speech-voicemail2text
pip install -r requirements.txt
```

### Run test cases
```bash
pytest ./tests/api_tests -k regression --capture=tee-sys
pytest ./tests/unit_tests
```

### Check HTML Report under reports folder

> [!NOTE]
> Currently default speech key and endpoint is set as a F0 pricing tier.
In order to change it's value, follow below steps:
  1. Navigate to _azure-ai-speech-voicemail2text_ -> _etc_ -> _config.properties_
  2. Modify the value of `speech_key` and `speech_region`

## Contact
If you have additional questions, please contact the Nuance V2T Migration Team: v2t-migration@microsoft.com, or your Account Representative.

## License
This project is licensed under the MIT License.

## Trademarks
This project may contain trademarks or logos for projects, products, or services. Authorized use of Microsoft trademarks or logos is subject to and must follow [Microsoft’s Trademark & Brand Guidelines](https://www.microsoft.com/en-us/legal/intellectualproperty/trademarks/usage/general). Use of Microsoft trademarks or logos in modified versions of this project must not cause confusion or imply Microsoft sponsorship. Any use of third-party trademarks or logos are subject to those third-party’s policies.

## Microsoft Open Source Code of Conduct
Please follow the [Microsoft Open Source Code of Conduct](https://opensource.microsoft.com/codeofconduct/) when using this product.