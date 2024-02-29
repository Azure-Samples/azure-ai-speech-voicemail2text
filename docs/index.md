# Voicemail to Text Integration Container (V2TIC)

When moving to cloud transcription technologies, Voicemail to Text Integration Container (V2TIC) saves you from having to reintegrate Nuance-managed Voicemail to Text (V2T) servers completely. V2TIC is an integration container that emulates existing integrations between voicemail servers and the Nuance V2T service. Instead of employing on-premises Nuance V2T, the backend recognition technology uses Microsoft's Azure AI (Congitive Services) Speech Recognition Service.

## Table of contents

- Introduction
  - [About](about/about.md)
  - [Architecture](about/architecture.md)
  - [Supported languages and formats](about/language-format-support.md)
- Build, deploy, and test the sample app
  - [Prerequisites](about/prerequisites.md)
  - [Configuration basics](configure/configure-basics.md)
  - [Build and deploy](build-deploy/build-summary.md)
  - [Test and validate](test-validate/test-validate.md)
- Manage V2TIC deployments
  - [Enable or disable autoscale](destroy-autoscale/autoscale.md)
  - [Destroy a deployment](destroy-autoscale/destroy.md)
- Configure V2TIC
  - [File descriptions](reference/file-descriptions.md)
  - [Configuration fields](reference/deploy-configurations-templates.md)
  - [Azure AI configurations](configure/configure-azure.md)
  - [Makefile information](reference/configure-makefile.md)
