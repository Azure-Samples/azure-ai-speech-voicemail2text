#By declaring targets as .PHONY, we ensure that the associated commands are always executed, regardless of the existence of files or directories with the same names as the targets.

.PHONY: default_make build_image check_minikube_status start_minikube load_image deploy_pod start_dashboard get_status destroy_pod enable_autoscale destroy_autoscale ssh_pod clean quick_start test_local test_pod test_deploy_pod test_quick_start_https test_clean

# Input speech key and endpoint tuple list (public or private) to get started
SPEECH_RESOURCES := "[('bac6a970e42345dc877be170eefc9c8b','wss://westus.stt.speech.microsoft.com/speech/universal/v2')]"
#SPEECH_RESOURCES := "[('bac6a970e42345dc877be170eefc9c8b','wss://westus.stt.speech.microsoft.com/speech/universal/v2'), ('05455fd708c344a5a326689856ab16fe','wss://eastus.stt.speech.microsoft.com/speech/universal/v2')]"

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
	pytest ./tests/api_tests -k regression --capture=tee-sys -s;\
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
    		minikube start --driver docker --force; \
    	fi

load_image:
	@eval export LOAD_IMAGE_NAME=$(image_name) ;\
	export tag_name="latest" ;\
	mkdir -p scratch ;\
	docker image save -o scratch/image.tar $$LOAD_IMAGE_NAME:$$tag_name ;\
	echo "Loading image $$LOAD_IMAGE_NAME ..."; \
	minikube image load scratch/image.tar ;\
	rm -rf scratch

kubectl_deploy_resource:
	@eval export source_file=$(source_file);\
	export destination_file=$(destination_file);\
	envsubst < $(source_file) > $(destination_file);\
	kubectl apply -f $(destination_file);\

deploy_pod:
	@export BASE_DIR=$(base_dir);\
	eval "export DEPLOYMENT=$(deployment)";\
	echo "Deploying $$DEPLOYMENT" ;\
	export DEPLOY_IMAGE_NAME=$(image_name);\
	export SPEECH_RESOURCES=$(SPEECH_RESOURCES);\
	if [ -z "$(base_dir)" ]; then\
		BASE_DIR=etc;\
	fi ;\
	echo $$DEPLOYMENT ;\
	if [ -z $(SPEECH_RESOURCES) ]; then\
		echo "SPEECH_RESOURCES was not provided, please review Makefile and ensure its value is not empty" && exit 1;\
	fi ;\
	base_deployment_dir=$$BASE_DIR/deployments/$$DEPLOYMENT;\
	echo "BASE_DIR: $$base_deployment_dir";\
	configmap_source=$$base_deployment_dir/configmap-file.yaml;\
	configmap_destination=$$base_deployment_dir/configmap-file-instance.yaml;\
	make kubectl_deploy_resource source_file=$$configmap_source destination_file=$$configmap_destination;\
	export v2tic_port=$$(kubectl get configmap $$DEPLOYMENT-configmap-file -o jsonpath='{.data.v2tic_port}') && \
	export v2tic_nodeport=$$(kubectl get configmap $$DEPLOYMENT-configmap-file -o jsonpath='{.data.v2tic_nodeport}') && \
	deployment_source=$$base_deployment_dir/deployment-file.yaml;\
	deployment_destination=$$base_deployment_dir/pod-file.yaml;\
	make kubectl_deploy_resource source_file=$$deployment_source destination_file=$$deployment_destination;\
	export vmcs_label=$$(kubectl get deployment $$DEPLOYMENT-deployment -o jsonpath='{.metadata.labels.app}') && \
	kubectl wait --for=condition=ready pod -l app=$$vmcs_label ;\
	export nodeport=$$(kubectl get configmap $$DEPLOYMENT-configmap-file -o jsonpath='{.data.v2tic_nodeport}') ;\
	if echo "$(OS_NAME)" | grep "Linux"; then\
		echo "Skipping port-forward on Linux" ;\
		export POD_IP=$$(kubectl get pod -l app=$$vmcs_label -o jsonpath='{.items[*].status.hostIP}') ;\
	else \
		kubectl port-forward service/$$DEPLOYMENT-service $$v2tic_nodeport:$$v2tic_port & \
		export POD_IP="127.0.0.1" ;\
	fi ;\
	echo pod_ip: "$$POD_IP" ;\
	echo node_port: "$$nodeport" ;\
	echo For deployment $$DEPLOYMENT send traffic to: "$$POD_IP:$$nodeport" ;\
	echo "" ;\
	echo "Refer README.md section 'Getting Started #6' to run sanity checks on created pod"

start_dashboard:
	minikube dashboard

get_status:
	kubectl get all

destroy_pod:
	@export DEPLOYMENT=$(deployment);\
	kubectl delete deployment.apps/$$DEPLOYMENT-deployment service/$$DEPLOYMENT-service configmap/$$DEPLOYMENT-configmap-file --force --grace-period=0

clean:
	@export DEPLOYMENT=$(deployment); \
	export BASE_DIR=$(base_dir);\
	if [ -z "$(base_dir)" ]; then\
		BASE_DIR=etc;\
	fi ;\
	base_deployment_dir=$$BASE_DIR/deployments/$$DEPLOYMENT;\
	echo "BASE_DIR: $$base_deployment_dir";\
	configmap_file_instance=$$base_deployment_dir/configmap-file-instance.yaml;\
	pod_file=$$base_deployment_dir/pod-file.yaml;\
	if [ -f "$$pod_file" ]; then \
    		echo "About to delete $$pod_file"; \
    		rm -f "$$pod_file"; \
    		echo "Deleted $$pod_file"; \
	else \
		echo "File $$pod_file doesn't exist. Skipping deletion."; \
	fi;\
	if [ -f "$$configmap_file_instance" ]; then \
    		echo "About to delete $$configmap_file_instance"; \
    		rm -f "$$configmap_file_instance"; \
    		echo "Deleted $$configmap_file_instance"; \
	else \
		echo "File $$configmap_file_instance doesn't exist. Skipping deletion."; \
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
	export BASE_DIR=$(base_dir);\
	if [ -z "$(base_dir)" ]; then\
		BASE_DIR=etc;\
	fi ;\
	if [ -z "$(image_name)" ]; then\
		IMAGE_NAME=$(DEFAULT_IMAGE_NAME)_$(shell date +'%Y%m%d-%H%M%S') ;\
	fi ;\
	docker build -t $$IMAGE_NAME . ;\
	echo "Image Name: $$IMAGE_NAME" ;\
	make start_minikube ;\
	make load_image image_name=$$IMAGE_NAME ;\
	make deploy_pod base_dir=$$BASE_DIR deployment=$$DEPLOYMENT image_name=$$IMAGE_NAME

display_pod_logs:
	@export POD_NAME=$(pod_name);\
	kubectl logs -f $$POD_NAME

test_pod:
	@echo "Running regression tests on pod.";\
	if echo "$(OS_NAME)" | grep "Linux"; then\
		pytest ./tests/api_tests -k podregression --capture=tee-sys --setup_local_server=False;\
	else \
		minikube delete ;\
		pytest ./tests/api_tests -k httppodregression --capture=tee-sys --setup_local_server=False;\
		minikube delete ;\
		pytest ./tests/api_tests -k smtppodregression --capture=tee-sys --setup_local_server=False;\
	fi	;\
	echo "Regression execution completed."