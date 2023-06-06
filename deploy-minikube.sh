#!/usr/bin/env bash

#gcloud config set project wdmproject23-v2

# Uncomment to create cluster
#gcloud container clusters create-auto app-cluster --region=europe-west4

#gcloud container clusters get-credentials app-cluster --region=europe-west4

#gcloud auth configure-docker

#kubectl config use-context gke_wdmproject23-v2_europe-west4_app-cluster

docker-compose build --no-cache

docker tag kafka-admin gcr.io/wdmproject23-v2/kafka-admin:latest
docker push gcr.io/wdmproject23-v2/kafka-admin:latest

docker tag order-rest2 gcr.io/wdmproject23-v2/order-rest-sql
docker push gcr.io/wdmproject23-v2/order-rest-sql

docker tag order-worker2 gcr.io/wdmproject23-v2/order-worker-sql
docker push gcr.io/wdmproject23-v2/order-worker-sql

docker tag stock-rest2 gcr.io/wdmproject23-v2/stock-rest-sql
docker push gcr.io/wdmproject23-v2/stock-rest-sql

docker tag stock-worker2 gcr.io/wdmproject23-v2/stock-worker-sql
docker push gcr.io/wdmproject23-v2/stock-worker-sql

docker tag payment-rest3 gcr.io/wdmproject23-v2/payment-rest-sql
docker push gcr.io/wdmproject23-v2/payment-rest-sql

docker tag payment-worker2 gcr.io/wdmproject23-v2/payment-worker-sql
docker push gcr.io/wdmproject23-v2/payment-worker-sql

cd k8s

kubectl apply -f zookeeper.yaml

sleep 15

kubectl apply -f kafka.yaml

sleep 15

kubectl apply -f kafka-admin.yaml

sleep 15

kubectl apply -f order-worker.yaml
kubectl apply -f stock-worker.yaml
kubectl apply -f payment-worker.yaml

sleep 15

kubectl apply -f order-rest.yaml
kubectl apply -f stock-rest.yaml
kubectl apply -f payment-rest.yaml

sleep 10

#gcloud compute forwarding-rules list
