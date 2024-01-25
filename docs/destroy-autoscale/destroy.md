# Destroy deployments

You can destroy V2TIC deployments if you need to make configuration changes or a pod needs to be deleted. Destroying a deployment deletes the deployment, service, and configmap for that deployment.

To a destroy a deployment, in your project, run this command, where `test_deployment` is the name of your deployment:

```bash
make destroy_pod deployment=test_deployment
```

[Return to table of contents](../index.md)