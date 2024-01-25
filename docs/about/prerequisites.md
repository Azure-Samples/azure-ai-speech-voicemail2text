# Prerequisites

Before you begin building and using V2TIC, you'll need these tools and libraries for building and deploying:
- [Docker](https://www.docker.com/). From instructions for preparing Docker for V2TIC, go to [Dockerfile](../../Dockerfile) in this project.
- [Minikube](https://github.com/kubernetes/minikube/releases/tag/v1.31.2)
    > [!NOTE]
    > This documentation uses minikube to set up and run a local Kubernetes environment. However, you can use other services instead.
- [kubectl](https://kubernetes.io/docs/tasks/tools/#kubectl) to verify and get information about builds from your CLI (you can also use Kubernetes Dashboard)
- An interface for configuring and running commands:
    - For Unbuntu users, we recommend:
        - Make
        - Shell
        - envsubst
    - For Windows users, we recommend installing Linux through [WSL](https://learn.microsoft.com/en-us/windows/wsl/install), then building through that subsystem.
- The Python libraries listed in [requirements.txt](../../requirements.txt)

You also need to have your Azure AI for Text to Speech resources set up, including:
- An Azure AI [subscription for Speech](https://azure.microsoft.com/en-us/pricing/details/cognitive-services/speech-services/)
- An Azure AI [endpoint](https://learn.microsoft.com/en-us/azure/ai-services/speech-service/speech-services-private-link?tabs=portal) for [Speech to Text REST API for short audio](https://learn.microsoft.com/en-us/azure/ai-services/speech-service/rest-speech-to-text-short)
- The URL and key for your endpoint.

To find out more about setting up and configuring Azure AI Speech services, go to the [documentation](https://learn.microsoft.com/en-us/azure/ai-services/speech-service/).

[Return to table of contents](../index.md)