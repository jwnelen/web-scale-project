#!/usr/bin/env bash

helm uninstall redis
helm uninstall nginx

cd k8s
kubectl delete -f .

# # Uncomment to delete cluster
#gcloud container clusters delete app-cluster --region=europe-west4