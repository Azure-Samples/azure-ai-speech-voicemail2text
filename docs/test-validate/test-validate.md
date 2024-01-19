# Test and validate

After building and deploying the image, you can test and validate it.

## Set SSH Tunneling Port Forwarding

Port forwarding is required for facilitating the connections from localhost to the pod of the minikube in which the services are running during your tests.

To set up the port number of your service deployment:
    
- Open the configmap-file.yaml for your service deployment, either `../etc/deployments/https/configmap-file.yaml` or `../etc/deployments/smtp/configmap-file.yaml`.
- Look for the port number on the `v2tic_nodeport` line. For example: `v2tic_nodeport= "31000"`
- Create the port forwarding connections by establishing SSH to minikube, and ensure the SSH tunneling sessions are always intact and live.
    - In a new screen, run this command, where `31000` and `32000` are the port numbers for your service deployments: `ssh -i ~/.minikube/machines/minikube/id_rsa docker@$(minikube ip) -L \*:31000:0.0.0.0:31000 -L \*:32000:0.0.0.0:32000`
You can close the screen after. 

## Start listeners for capturing responses

V2TIC has listeners for capturing responses in order to see and test those responses. Listener files are found in `sample-server-listeners`.

In order to send responses to listeners, you need to change the destination in your V2TIC deployment configuration to the listener port. Once you've finished testing, you must change them back to the real destination values.

(what and how to change those values)

To start the listener script for each deployment:

### HTTPS

In a new terminal, run this command in the V2TIC project folder:

```
ent-v2t-azure$ /usr/bin/python3.9 sample_server_listeners/sample_http_server.py
```

You should see in response, where the IP address is the address for your V2TIC server:

```
HTTP Server listening for responses on http://10.33.135.37:8443/response
```

Responses will appear in this terminal.

### SMTP

In a new terminal. run this command in the V2TIC project folder:

```
/ent-v2t-azure$ /usr/bin/python3.9 sample_server_listeners/sample_smtp_server.py
```

You should see in response, where the IP address is the address for your V2TIC server:

```
SMTP Server Listening On 10.33.135.37:9025
```

Responses will appear in this terminal.

## Test your services

You can run local and remote tests to verify your builds and port forwarding are working. You'll need the sample audio file found at `../etc/audio/sample-audio.txt`` to run these tests.

### Test your HTTPS service

#### Local

- In your project, either run the test script located at `sample_clients/sample_https_client.py` to request a transcription, or use the curl command below. In this command,`31000` is your service deployment's port number and `10.33.135.37:8443` is the IP address and port for the listener:

```
curl -X PUT -vN https://127.0.0.1:31000/transcribe  -k -H "X-Reference: testing-http-push" -H "Connection: close" -H "Content-Type: audio/wav" -H "X-Language: en-US" -H "X-Return-URL:  http://10.33.135.37:8443/response" -H "Content-Transfer-Encoding: base64" -H "X-Caller: 1234567890" -d @etc/audio/sample-audio.txt
```
- In the listener terminal, check the response for a `conversionResponse` message. The `Location` value matches the request ID (`scrid`).
- You can also check for transcription response on the service container logs with a kubectl command or the Kubernetes Dashboard:
    - kubectl:
        - In your project, run `kubectl get pod` to display the pod's information. The pod's name, ready status, status, restarts, and age appears.
        - Run `kubectl logs` with the pod's name to display the logs. For example: `kubectl logs test_pod`
    - Kubernetes Dashboard:
        - Follow the Kubernetes Dashboard instructions [verify build instructions](../build-deploy/build-summary.md#kubernetes-dashboard) to view the transcription response logs.

#### Remote

- Copy `sample-audio.txt` to another host and make sure it's accessible.
- In your project, run this command, where `31000` is your service deployment's port number and `http://10.33.135.37:8443` is the secure V2TIC address, which is the same address as the listener, and the port configured for the listener:

```
curl -X PUT -vN https://<Docker_IP>:31000/transcribe  -k -H "X-Reference: testing-http-push" -H "Connection: close" -H "Content-Type: audio/wav" -H "X-Language: en-US" -H "X-Return-URL: http://10.33.135.37:8443/response" -H "Content-Transfer-Encoding: base64" -H "X-Caller: 1234567890" -d @audio/sample-audio.txt
```

- In the listener terminal, check the response for a `conversionResponse` message. The `Location` value matches the request ID (`scrid`).
- Check for transcription response on the service container logs with a kubectl command or the Kubernetes Dashboard:
    - kubectl:
        - In your project, run `kubectl get pod` to display the pod's information. The pod's name, redy status, status, restarts, and age appears.
        - Run `kubectl logs` with the pod's name to display the logs. For example: `kubectl logs test_pod`
    - Kubernetes Dashboard:
        - Follow the Kubernetes Dashboard instructions [verify build instructions](../build-deploy/build-summary.md) to view the transcription response logs.

### Test your SMTP service

#### Local

- From your localhost, run `sample_smtp_client.py` found at `/sample_smtp_clients/sample_smtp_client.py`.
- In the listener terminal, check the response for a `conversionResponse` message. The `Location` value matches the request ID (`scrid`).
- Check for transcription response on the service container logs with a kubectl command or the Kubernetes Dashboard:
    - kubectl:
        - In your project, run `kubectl get pod` to display the pod's information. The pod's name, ready status, status, restarts, and age appears.
        - Run `kubectl logs` with the pod's name to display the logs. For example: `kubectl logs test_pod`
    - Kubernetes Dashboard:
        - Follow the Kubernetes Dashboard instructions [verify build instructions](../build-deploy/build-summary.md) to view the transcription response logs.

#### Remote

> [!NOTE]
> Requires the aiosmptlib library in addition to Python3.

- Copy `sample_smtp_client.py` found at `/sample_smtp_clients/sample_smtp_client.py` to another host.
- In `sample_smtp_client.py`, edit the `smtp_server` to the address of `smtp_server` in your V2TIC deployment.
- Run `sample_smtp_client.py` on your other host using this command: `/usr/bin/python3 sample_smtp_clients/sample_smtp_client.py`
- Check for transcription response on the service container logs with a kubectl command or the Kubernetes Dashboard:
    - kubectl:
        - In your project, run `kubectl get pod` to display the pod's information. The pod's name, ready status, status, restarts, and age appears.
        - Run `kubectl logs` with the pod's name to display the logs. For example: `kubectl logs test_pod`
    - Kubernetes Dashboard:
        - Follow the Kubernetes Dashboard instructions [verify build instructions](../build-deploy/build-summary.md) to view the transcription response logs.

## Check and debug deployments

To check the status of a deployment, run `kubectly get all` in the V2TIC project to list the status of the cluster. The first section lists the pod names and their status:

```
    /ent-v2t-azure# kubectl get all
    NAME                                    READY   STATUS             RESTARTS      AGE
    pod/https-deployment-7468cf8b6b-zvstl   1/1     Running            1 (20h ago)   20h
    pod/smtp-deployment-8c74fb5c6-9lgd8     0/1     CrashLoopBackOff   2 (19s ago)   35s
```

<p>To see the logs for a specific pod, run <tt>kubectl logs &lt;pod/service-deployment&gt;</pod></tt>:</p>

```
    ent-v2t-azure# kubectl logs -f pod/smtp-deployment-8c74fb5c6-9lgd8
Traceback (most recent call last):
  File "/app/servers/smtp_server.py", line 9, in &lt;module&gt;
    import Common.request_handler as request_handler
  File "/app/Common/request_handler.py", line 3, in &lt;module&gt;
    from Common.response_creator import ResponseCreator
  File "/app/Common/response_creator.py", line 1, in &lt;module&gt;
    from v2ticlib.template_utils import template_utils
  File "/app/v2ticlib/template_utils.py", line 144, in &lt;module&gt;
    template_utils: Final[TemplateUtils] = TemplateUtils()
  File "/app/v2ticlib/template_utils.py", line 36, in __init__
    self._templates[template] = self._environment.get_template(template)
  File "/usr/local/lib/python3.9/dist-packages/jinja2/environment.py", line 1010, in get_template
    return self._load_template(name, globals)
  File "/usr/local/lib/python3.9/dist-packages/jinja2/environment.py", line 969, in _load_template
    template = self.loader.load(self, name, self.make_globals(globals))
  File "/usr/local/lib/python3.9/dist-packages/jinja2/loaders.py", line 138, in load
    code = environment.compile(source, name, filename)
  File "/usr/local/lib/python3.9/dist-packages/jinja2/environment.py", line 768, in compile
    self.handle_exception(source=source_hint)
  File "/usr/local/lib/python3.9/dist-packages/jinja2/environment.py", line 936, in handle_exception
    raise rewrite_traceback_stack(source=source)
  File "/app/etc/profiles/sample_smtp/templates/response_body.j2", line 12, in template
    converted_text: {{This person called and left you a message. Please call voicemail - Nuance}}
jinja2.exceptions.TemplateSyntaxError: expected token 'end of print statement', got 'person '
```

[Return to table of contents](../index.md)