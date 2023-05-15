#!/usr/bin/env bash

helm uninstall redis

cd k8s
kubectl delete -f .

gcloud container clusters delete app-cluster --region=europe-west4