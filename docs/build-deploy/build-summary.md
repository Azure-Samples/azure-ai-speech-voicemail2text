# Build and deploy a sample V2TIC

In order to deploy V2TIC, you need to configure, build, and load the V2TIC image for HTTPS or SMTP services. This topic guides you through building and loading locally or on a remote host using the provided sample files. You can also use these sample files as templates for your own deployments.

To get started on configuring your own V2TIC deployment, go to [Configuration basics](../configure/configure-basics.md).

> [!NOTE]
> This documentation uses minikube to set up and run a local Kubernetes environment. However, you can adapt these steps for other services.

Here's a quick look at what to do:
- Clone V2TIC onto the server where you want to host V2TIC.
- Make sure you have all the [prerequisites](../about/prerequisites.md).
- Start minikube.
- Build the image.
- Load the image.
- Deploy the image.
- Verify the build.

The commands in this process use the actions defined in [Makefile](../reference/configure-makefile.md) in the project.

## Clone the project

Clone the project from GitHub. The location should be on the server where you want to host the V2TIC API.

## Start minikube

Before you can build your V2TIC image, you need a Kubernetes environment.

To start minikube, in your CLI, run:
```bash
make start_minikube
```
or
```bash
minikube start --force --driver docker
```

You can verify your Kubernetes is running with:
```bash
make check_minikube_status
```
or
```bash
minikube status
```

For more information on running minikube, go to the [minikube documentation](https://minikube.sigs.k8s.io/docs/).

## Build the image

Once you have a local Kubernetes environment, you can build the V2TIC image.

Before you can build the image, you must enter the speech key (`SPEECH_KEY`) and end point (`END_POINT`) values for your Azure AI in [Makefile](../reference/configure-makefile.md).
    
Building a V2TIC image is necessary for the initial deployment, as well as whenever you make configuration changes. This is because building an image creates configuration and deployment files for that specific image (`configmap-file-instance.yaml` and `pod-file.yaml`). To terminate a build, go to [Destroy deployments](../destroy-autoscale/destroy.md).
    
- In your CLI, navigate to the V2TIC project folder.
- Build the Docker image by running `make build_image`. You can add `image_name=` to name your image. For example:
    ```bash
    make build_image image_name=test_image
    ```
    Otherwise, the image name defaults to whatever is specified in `Makefile`.

## Load the image

To load the Docker image into minikube:
Run
```bash
make load_image image_name=test_image
```
where `test_image` is the name of your image.

## Deploy the image

You can deploy the image for HTTPS or SMTP services. To deploy:
    
- Check for a folder under `etc/deployments`. Make sure it contains `HTTPS` and `SMTP` folders, and that each folder contains a `configmap-file.yaml` and `deployment-file.yaml.` The V2TIC repo contains sample files for both HTTPS and SMTP deployments that you can use and modify. For more information on configuring these files, go to [Configuration fields](../reference/deploy-configurations-templates.md).
- `Run make deploy_pod` to deploy and expose the services (HTTPS or SMTP) on Kubernetes:
    - For HTTPS: `make deploy_pod deployment=https image_name=test_image`
    - For SMTP: `make deploy_pod deployment=smtp image_name=test_image`

## Verify the build

After building and deploying the image, verify the build with either kubectl commands or Kubernetes Dashboard.

### Kubernetes commands

- In `ent-v2t-azure`, run `kubectl cluster-info` to display the cluster information.
- Run `kubectl get pod` to display the pod information.
- Run `kubectl get deployment` to get deployment information.
- Run `kubectl get service` to get service information.

### Kubernetes Dashboard

- In `ent-v2t-azure`, run `make start_dashboard`.
- Go to the URL that appears to open the dashboard.
- Go to the **Deployments** and **Pods** tabs to validate and see information about your builds.
    - In **Pods**, click on the deployment **Name**, then the **Logs** icon.
    [location of the Logs icon](../images/kubernetes-dashboard-logs.png)
- Go to the **Services** tab to validate and see information about each deployed service.

Once you've built and verified your image, you can [test and validate](../test-validate/test-validate.md) the build.

[Return to table of contents](../index.md)