#!/usr/bin/env bash

helm uninstall redis

cd k8s
kubectl delete -f .

minikube stop