#!/usr/bin/env bash

gcloud config set project wdmproject23-v2

# Uncomment to create cluster
gcloud container clusters create-auto app-cluster --region=europe-west4

gcloud container clusters get-credentials app-cluster --region=europe-west4

gcloud auth configure-docker

kubectl config use-context gke_wdmproject23-v2_europe-west4_app-cluster

docker-compose build

docker tag kafka-admin gcr.io/wdmproject23-v2/kafka-admin:latest
docker push gcr.io/wdmproject23-v2/kafka-admin:latest


docker tag order-rest gcr.io/wdmproject23-v2/order-rest:latest
docker push gcr.io/wdmproject23-v2/order-rest:latest

docker tag order-worker gcr.io/wdmproject23-v2/order-worker:latest
docker push gcr.io/wdmproject23-v2/order-worker:latest

docker tag stock-rest gcr.io/wdmproject23-v2/stock-rest:latest
docker push gcr.io/wdmproject23-v2/stock-rest:latest

docker tag stock-worker gcr.io/wdmproject23-v2/stock-worker:latest
docker push gcr.io/wdmproject23-v2/stock-worker:latest

docker tag payment-rest gcr.io/wdmproject23-v2/payment-rest:latest
docker push gcr.io/wdmproject23-v2/payment-rest:latest

docker tag payment-worker gcr.io/wdmproject23-v2/payment-worker:latest
docker push gcr.io/wdmproject23-v2/payment-worker:latest


cd k8s

kubectl apply -f zookeeper.yaml

sleep 10

kubectl apply -f kafka.yaml

sleep 10

kubectl apply -f order-db.yaml
kubectl apply -f stock-db.yaml
kubectl apply -f payment-db.yaml

sleep 15

kubectl apply -f kafka-admin.yaml

sleep 15

kubectl apply -f order-db.yaml
kubectl apply -f stock-db.yaml
kubectl apply -f payment-db.yaml

sleep 15

kubectl apply -f order-worker.yaml
kubectl apply -f stock-worker.yaml
kubectl apply -f payment-worker.yaml

sleep 15

kubectl apply -f order-rest.yaml
kubectl apply -f stock-rest.yaml
kubectl apply -f payment-rest.yaml

sleep 10

gcloud compute forwarding-rules list
