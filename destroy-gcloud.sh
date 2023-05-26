#!/usr/bin/env bash

gcloud config set project wdmproject23-v2
gcloud container clusters get-credentials app-cluster --region=europe-west4
gcloud auth configure-docker
kubectl config use-context gke_wdmproject23-v2_europe-west4_app-cluster

#helm uninstall nginx

cd k8s-gcloud
kubectl delete -f .

# # Uncomment to delete cluster
#gcloud container clusters delete app-cluster --region=europe-west4