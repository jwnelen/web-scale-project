#!/usr/bin/env bash

helm uninstall redis
helm uninstall nginx

cd k8s
kubectl delete -f .

# Comment this out when testing, it will save a lot of time!
gcloud container clusters delete app-cluster --region=europe-west4