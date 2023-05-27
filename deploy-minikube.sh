#!/usr/bin/env bash

#minikube start
#minikube dashboard &

kubectl config use-context minikube
# Fixes a bug on ubuntu
kubectl delete -A ValidatingWebhookConfiguration ingress-nginx-admission

eval $(minikube docker-env)

docker-compose build

cd k8s

kubectl apply -f order-db.yaml
kubectl apply -f stock-db.yaml
kubectl apply -f user-db.yaml

sleep 10

kubectl apply -f order-app.yaml
kubectl apply -f stock-app.yaml
kubectl apply -f user-app.yaml

sleep 10

kubectl apply -f ingress-service.yaml
minikube tunnel
