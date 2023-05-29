#!/usr/bin/env bash

kubectl config use-context minikube
# Fixes a bug on ubuntu
kubectl delete -A ValidatingWebhookConfiguration ingress-nginx-admission
eval $(minikube docker-env)

docker-compose build stock-worker-service
docker-compose build stock-rest-service
docker-compose build kafka-admin-service

docker tag kafka-admin gcr.io/wdmproject23-v2/kafka-admin:latest
docker push gcr.io/wdmproject23-v2/kafka-admin:latest

docker tag stock-rest gcr.io/wdmproject23-v2/stock-rest:latest
docker push gcr.io/wdmproject23-v2/stock-rest:latest

docker tag stock-worker gcr.io/wdmproject23-v2/stock-worker:latest
docker push gcr.io/wdmproject23-v2/stock-worker:latest


cd k8s

kubectl apply -f zookeeper.yaml

sleep 15

kubectl apply -f kafka.yaml

sleep 15


kubectl apply -f stock-db.yaml

sleep 15

kubectl apply -f kafka-admin.yaml

sleep 15

kubectl apply -f stock-worker.yaml

sleep 10

kubectl apply -f stock-rest.yaml


minikube tunnel
