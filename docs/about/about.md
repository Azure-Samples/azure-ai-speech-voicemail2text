 # About Voicemail to Text Integration Container (V2TIC)

Voicemail to Text (V2T) is a speech recognition service that transcribes voice messages from a voicemail server into text, allowing the end user to read their voice messages instead of listening to them.

Voicemail to Text Integration Container (V2TIC) is an integration container that emulates existing integrations between voicemail servers and the Nuance-managed Voicemail to Text (V2T) service. Instead of employing on-premises Nuance V2T, the backend recognition technology uses [Azure AI services](https://learn.microsoft.com/en-us/azure/ai-services/what-are-ai-services). This emulation eliminates the need for reintegrating existing voicemail servers to a new transcription service for Nuance V2T clients moving to cloud technologies.

The project contains the files for building and deploying V2TIC, as well as sample files for running basic deployments or to base your own deployments on.

This documentation is for technical users of existing Nuance V2T integrations, and assumes readers are familiar with the tools and languages used for setting up and deploying V2TIC. Such as:
- Developers
- Technical Support Personnel
- System Administrators
    
Users can assess how to adapt these examples to their own container orchestration framework. 

## Benefits for end users

V2TIC's benefits to end users include:
- No need to write messages down – a paperless environment.
- Read messages in email or visual voicemail applications.
- Automatically capture caller details.
- Screen calls and determine the urgency of a response.
- Reply directly in the same channel.
- React quickly to messages.
- No navigation through voicemail menus.
- Zero maintenance mailbox.

## Benefits for partners

V2TIC is flexible and can quickly and easily be integrated with a broad range of platforms and services. Using HTTPS and TLS v1.3, voice messages are securely transferred to the Azure AI Services (ACS) speech-to-text for processing, with the resulting transcription returned in a secure manner.

## Use cases

Voicemail to Text fits all situations such as:
- Discreetly review who called and what they said.
- Easily respond or forward messages to others.
- Never miss an important message while in a meeting or on the phone.
- Manage voicemails the same way you manage your email: file voicemails for future reference, flag for follow up, or mark as spam.

[Return to table of contents](../index.md)