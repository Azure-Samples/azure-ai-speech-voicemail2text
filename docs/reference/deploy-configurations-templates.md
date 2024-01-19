# Configuration fields

The V2TIC message request and conversion response formats are the same as for Nuance V2T. Configurations for these are stored in the `configmap-file.yaml` for individual deployments and globally in `config.properties`. `configmap-file.yaml` values override global settings.

> [!NOTE]
> You cannot make changes to an active V2TIC deployment. This is because building a deployment creates an instance of the configuration files and does not continuously update to new configurations. To make a change to a configuration, such as changing a port number, you must [destroy the active deployment](../destroy-autoscale/destroy.md) and [build a new image](../build-deploy/build-summary.md).

## Global configuration config.properties

- [v2tic]: settings section for V2TIC environment such as logging, ports, etc.
    - logging_level=
    - port=9443
    - host=127.0.0.1
    - cert_file=etc/certs/certificate.pem
    - key_file=etc/certs/private_key.pem
    - consume_request_timeout=5 seconds
    - coroutine_execution_default_timeout=10 seconds
    
- [transcoder]: Settings for transcoder in Linux.
- [language_configuration]: Supported languages.
- [ejector]: Time settings for delivery.
- [smtp]: Settings section for the SMTP response channel such host, port, and efault SMTP commands.
- [profiles]: Path and file name of the profile deployment.
- [acs_client]: Settings for Azure AI speech-to-text. Go to [Configure Azure](../configure/configure-azure.md) for additional configuration.
    - profanity_option= Specifies how to handle profanity in recognition results (masked, raw, removed.) Default is masked.
    - word_level_confidence=False
    - display_word_timings=False
    - silence.use_default_values=False
        - The following silence properties are applied when silence.use_default_values=false :
            - silence.segment_silence_timeout=1000 ms
            - silence.initial_silence_timeout=5000 ms (The start of the audio stream contained only silence, and the service timed out while waiting for speech.)
            - segmentation_forced_timeout=45000 ms (Azure AI recommended.)

## HTTPS configmap-file.yaml

- apiVersion: v1
- kind: ConfigMap
    - name: Name of the configmap. Must match the `name` under `configMapRef` in `deployment.yaml`.

- v2tic_logging_level: Logging level
- v2tic_nodeport: Incoming port for receiving requests from voicemail server. Used for port forwarding as required. The range of valid ports is 30000-32767.
- v2tic_port: Outgoing port for sending final responses.
- v2tic_host: IP address of the V2TIC server.
- v2tic_cert_file: Location of the security certificate for incoming requests.
- v2tic_key_file: Location of the private key for incoming requests.
- v2tic_consume_request_timeout: Timeout for consuming incoming requests.
- v2tic_coroutine_execution_default_timeout: Default timeout.

- profiles_folder: Path to the profile folder for this deployment.</li>
- profiles_profile: Location and class name of the profile.</li>
    
- **Only applicable in linux**:    transcoder_terminate_after:
- **Only applicable in linux**: .. 2 seconds after the initial 10
        transcoder_kill_after:
    
    metadata_default_language: Default language for transcription.
- metadata_default_lid_languages: If language ID is enabled in acs settings, the list of applicable languages.
- metadata_default_thresholds: The minimum confidence level for transcription success and the maximum length of allowed transcription.
- metadata_default_lid_thresholds: In the case of multiple languages, the minimum confidence level for transcription success and the maximum length of allowed transcription.
- metadata_log_transcriptions_enabled: Whether to log transcriptions.
- metadata_truncate_lenghty_transcriptions_enabled: Whether to cut off a transcription once it's reached the maximum length.
- metadata_max_transcription_length: Maximum character length of transcription.

- ejector_max_attempts: Maximum allowed ejector attempts.
- ejector_wait_exponential_multiplier: "2"
- ejector_wait_exponential_min: 0.5 seconds
- ejector_wait_exponential_max: 2 seconds
- ejector_retry_on_exception example for http exceptions:OSError,http.client.HTTPException
- ejector_retry_on_exception example for smtp exceptions:ValueError,aiosmtplib.SMTPException
- ejector_retry_on_exception: Whether to retry ejector when an exception occurs.

For Azure AI (`acs_client`) fields, go to [Azure AI configurations](../configure/configure-azure.md).

## SMTP configmap-file.yaml

- apiVersion: v1
- kind: ConfigMap
    - name: Name of the configmap. Must match the `name` under `configMapRef` in `deployment.yaml`.

- v2tic_logging_level: Logging level
- v2tic_nodeport: Incoming port for receiving requests from voicemail server. Used for port forwarding as required. The range of valid ports is 30000-32767.
- v2tic_port: Outgoing port for sending final responses.
- v2tic_host: IP address of the V2TIC server.
- v2tic_cert_file: Location of the security certificate for incoming requests.
- v2tic_key_file: Location of the private key for incoming requests.
- v2tic_consume_request_timeout: Timeout for consuming incoming requests.
- v2tic_coroutine_execution_default_timeout: Default timeout.

- smtp_client_cert_file: Location of the security certificate for outgoing responses.
- smtp_client_key_file: Location of the key for outgoing responses.
- smtp_response_port: Port for sending final responses.
- smtp_response_host: IP address for sending the final response.
- smtp_default_response_from: Default value for "from" of the final response (such as an email sender).
- smtp_default_response_subject: Subject for the final response.

- profiles_folder: Path to the profile folder for this deployment.
- profiles_profile: Location and class name of the profile.
    
- **Only applicable in linux**: transcoder_terminate_after:
- **Only applicable in linux**: .. 2 seconds after the initial 10
        transcoder_kill_after:

- metadata_default_language: Default language for transcription.
- metadata_default_lid_languages: If language ID is enabled in acs settings, the list of applicable languages.
- metadata_default_thresholds: The minimum confidence level for transcription success and the maximum length of allowed transcription.
- metadata_default_lid_thresholds: In the case of multiple languages, the minimum confidence level for transcription success and the maximum length of allowed transcription.
- metadata_log_transcriptions_enabled: Whether to log transcriptions.
- metadata_truncate_lenghty_transcriptions_enabled: Whether to cut off a transcription once it's reached the maximum length.
- metadata_max_transcription_length: Maximum character length of transcription.

- ejector_max_attempts: Maximum allowed ejector attempts.
- ejector_wait_exponential_multiplier: "2"
- ejector_wait_exponential_min: 0.5 seconds
- ejector_wait_exponential_max: 2 seconds
- ejector_retry_on_exception example for http exceptions:OSError,http.client.HTTPException
- ejector_retry_on_exception example for smtp exceptions:ValueError,aiosmtplib.SMTPException
- ejector_retry_on_exception: Whether to retry ejector when an exception occurs.

For Azure AI (`acs_client`) fields, go to [Azure AI configurations](../configure/configure-azure.md).

[Return to table of contents](../index.md)