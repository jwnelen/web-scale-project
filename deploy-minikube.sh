#!/usr/bin/env bash

eval $(minikube docker-env)

docker-compose build

helm repo add bitnami https://charts.bitnami.com/bitnami

helm repo update

helm install -f helm-config/redis-helm-values.yaml redis bitnami/redis

cd k8s
kubectl apply -f .

minikube tunnel
