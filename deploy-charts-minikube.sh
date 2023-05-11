#!/usr/bin/env bash

helm repo add bitnami https://charts.bitnami.com/bitnami
helm repo update

helm install my-release oci://registry-1.docker.io/bitnamicharts/mongodb
# helm install -f helm-config/redis-helm-values.yaml redis bitnami/redis