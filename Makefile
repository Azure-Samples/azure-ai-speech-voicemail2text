#By declaring targets as .PHONY, we ensure that the associated commands are always executed, regardless of the existence of files or directories with the same names as the targets.

.PHONY: default_make build_image check_minikube_status start_minikube load_image deploy_pod start_dashboard get_status destroy_pod enable_autoscale destroy_autoscale ssh_pod clean quick_start test_local

# Input speech key and endpoint tuple list (public or private) to get started
SPEECH_RESOURCES := [('bac6a970e42345dc877be170eefc9c8b','wss://westus.stt.speech.microsoft.com/speech/universal/v2')]
#SPEECH_RESOURCES := [('bac6a970e42345dc877be170eefc9c8b','wss://westus.stt.speech.microsoft.com/speech/universal/v2'), ('05455fd708c344a5a326689856ab16fe','wss://eastus.stt.speech.microsoft.com/speech/universal/v2')]

# Provide a value of IMAGE_NAME= while calling target build_image, else it will default to 'default_image_<datetimestamp>'
# Eg: make build_image image_name=image_vmcs_01
MAKEFLAGS += --no-print-directory

DEFAULT_IMAGE_NAME ?= default_image

.DEFAULT_GOAL := default_make

OS_NAME := $(shell uname)

default_make:
	@echo "No targets provided! Please consider re-running make with target as an argument, Eg: make build_image or make deploy_pod"

test_local:
	@echo "Running regression tests locally.";\
	pytest ./tests/api_tests -k regression --capture=tee-sys;\
	echo "Regression execution completed."
	@echo "Running unit tests locally.";\
	pytest ./tests/unit_tests

build_image:
	@eval "export IMAGE_NAME=$(if $(image_name),$(image_name),$(DEFAULT_IMAGE_NAME))_$(shell date +'%Y%m%d-%H%M%S')";\
    docker build -t $$IMAGE_NAME . ;\
	echo "Image Name: $$IMAGE_NAME"

check_minikube_status:
	@minikube status

MINIKUBE_STATUS := $(shell minikube status)

start_minikube:
	@echo "Minikube status: $(MINIKUBE_STATUS)"
	@if echo "$(MINIKUBE_STATUS)" | grep -q "Running"; then \
    		echo "Minikube is already running"; \
	else \
    		minikube start --driver docker; \
    	fi

load_image:
	@eval export LOAD_IMAGE_NAME=$(image_name) ;\
	export tag_name="latest" ;\
	mkdir -p scratch ;\
	docker image save -o scratch/image.tar $$LOAD_IMAGE_NAME:$$tag_name ;\
	echo "Loading image $$LOAD_IMAGE_NAME ..."; \
	minikube image load scratch/image.tar ;\
	rm -rf scratch

deploy_pod:
	@eval export DEPLOYMENT=$(deployment);\
	export DEPLOY_IMAGE_NAME=$(image_name);\
	export SPEECH_RESOURCES=$(SPEECH_RESOURCES);\

	echo $$DEPLOYMENT ;\
	if [ -z "$(SPEECH_RESOURCES)" ]; then\
		echo "SPEECH_RESOURCES was not provided, please review Makefile and ensure its value is not empty" && exit 1;\
	fi ;\
	envsubst < etc/deployments/$$DEPLOYMENT/configmap-file.yaml > etc/deployments/$$DEPLOYMENT/configmap-file-instance.yaml ;\
	kubectl apply -f etc/deployments/$$DEPLOYMENT/configmap-file-instance.yaml;\
	export v2tic_port=$$(kubectl get configmap $$DEPLOYMENT-configmap-file -o jsonpath='{.data.v2tic_port}') && \
	export v2tic_nodeport=$$(kubectl get configmap $$DEPLOYMENT-configmap-file -o jsonpath='{.data.v2tic_nodeport}') && \
	envsubst < etc/deployments/$$DEPLOYMENT/deployment-file.yaml > etc/deployments/$$DEPLOYMENT/pod-file.yaml ;\
	kubectl apply -f etc/deployments/$$DEPLOYMENT/pod-file.yaml;\
	export vmcs_label=$$(kubectl get deployment $$DEPLOYMENT-deployment -o jsonpath='{.metadata.labels.app}') && \
	kubectl wait --for=condition=ready pod -l app=$$vmcs_label ;\
	export nodeport=$$(kubectl get configmap $$DEPLOYMENT-configmap-file -o jsonpath='{.data.v2tic_nodeport}') ;\
	echo "Refer README.md section 'Getting Started #6' to run sanity checks on created pod";\
	echo node_port: "$$nodeport" ;\
	if echo "$(OS_NAME)" | grep "Linux"; then\
		export pod_ip="$$(kubectl get pod -l app=$$vmcs_label -o jsonpath='{.items[*].status.hostIP}')" ;\
		echo pod_ip: "$$pod_ip" ;\
		echo For deployment $$DEPLOYMENT send traffic to "$$pod_ip:$$nodeport" ;\
		echo "Skipping port-forward on Linux" ;\
	else \
		echo pod_ip: "127.0.0.1" ;\
		kubectl port-forward service/$$DEPLOYMENT-service $$v2tic_nodeport:$$v2tic_port;\
	fi

start_dashboard:
	minikube dashboard

get_status:
	kubectl get all

destroy_pod:
	@export DEPLOYMENT=$(deployment);\
	kubectl delete deployment.apps/$$DEPLOYMENT-deployment service/$$DEPLOYMENT-service configmap/$$DEPLOYMENT-configmap-file

clean:
	@export DEPLOYMENT=$(deployment); \
	if [ -f "etc/deployments/$$DEPLOYMENT/pod-file.yaml" ]; then \
    		echo "About to delete etc/deployments/$$DEPLOYMENT/pod-file.yaml"; \
    		rm -f "etc/deployments/$$DEPLOYMENT/pod-file.yaml"; \
    		echo "Deleted pod-file.yaml"; \
	else \
		echo "File etc/deployments/$$DEPLOYMENT/pod-file.yaml doesn't exist. Skipping deletion."; \
	fi;\
	if [ -f "etc/deployments/$$DEPLOYMENT/configmap-file-instance.yaml" ]; then \
    		echo "About to delete etc/deployments/$$DEPLOYMENT/configmap-file-instance.yaml"; \
    		rm -f "etc/deployments/$$DEPLOYMENT/configmap-file-instance.yaml"; \
    		echo "Deleted configmap-file-instance.yaml"; \
	else \
		echo "File etc/deployments/$$DEPLOYMENT/configmap-file-instance.yaml doesn't exist. Skipping deletion."; \
	fi ;\
	rm -rf scratch

enable_autoscale:
	@export DEPLOYMENT=$(deployment);\
	minikube addons enable metrics-server ;\
	kubectl autoscale deployment $$DEPLOYMENT-deployment --cpu-percent=30 --min=1 --max=10

destroy_autoscale:
	@export DEPLOYMENT=$(deployment);\
	kubectl delete horizontalpodautoscaler.autoscaling/$$DEPLOYMENT-deployment

ssh_pod:
	@export POD_NAME=$(pod_name);\
	kubectl exec -it $$POD_NAME -- /bin/bash

quick_start:
	@export DEPLOYMENT=$(deployment);\
	export IMAGE_NAME=$(DEFAULT_IMAGE_NAME)_$(shell date +'%Y%m%d-%H%M%S') ;\
	docker build -t $$IMAGE_NAME . ;\
	echo "Image Name: $$IMAGE_NAME" ;\
	make start_minikube ;\
	make load_image image_name=$$IMAGE_NAME ;\
	make deploy_pod deployment=$$DEPLOYMENT image_name=$$IMAGE_NAME

display_pod_logs:
	@export POD_NAME=$(pod_name);\
	kubectl logs -f $$POD_NAME
