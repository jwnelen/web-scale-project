#!/usr/bin/env bash

gcloud config set project wdmproject23-v2

# Uncomment to create cluster
gcloud container clusters create-auto app-cluster --region=europe-west4

gcloud container clusters get-credentials app-cluster --region=europe-west4

gcloud auth configure-docker

kubectl config use-context gke_wdmproject23-v2_europe-west4_app-cluster

docker-compose build stock-worker-service
docker-compose build stock-rest-service

docker tag stock-rest gcr.io/wdmproject23-v2/stock-rest:latest
docker push gcr.io/wdmproject23-v2/stock-rest:latest

docker tag stock-worker gcr.io/wdmproject23-v2/stock-worker:latest
docker push gcr.io/wdmproject23-v2/stock-worker:latest


cd k8s

kubectl apply -f zookeeper.yaml

sleep 15

kubectl apply -f kafka.yaml

sleep 20

kubectl apply -f stock-db.yaml

sleep 10

kubectl apply -f stock-rest.yaml

sleep 10

kubectl apply -f stock-worker.yaml

sleep 10

gcloud compute forwarding-rules list
