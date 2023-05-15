#!/usr/bin/env bash

cd k8s
kubectl delete -f .

gcloud container clusters delete app-cluster --region=europe-west4