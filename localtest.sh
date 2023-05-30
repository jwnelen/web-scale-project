#!/usr/bin/env bash

#start minikube and mount credentials
#minikube start --mount --mount-string="/home/USERNAME/.config/gcloud:/tmp/google_key"

kubectl config use-context minikube

eval $(minikube docker-env)

docker-compose build

docker tag kafka-admin gcr.io/wdmproject23-v2/kafka-admin:latest
docker push gcr.io/wdmproject23-v2/kafka-admin:latest

docker tag stock-rest gcr.io/wdmproject23-v2/stock-rest:latest
docker push gcr.io/wdmproject23-v2/stock-rest:latest

docker tag stock-worker gcr.io/wdmproject23-v2/stock-worker:latest
docker push gcr.io/wdmproject23-v2/stock-worker:latest

#docker tag payment-rest gcr.io/wdmproject23-v2/payment-rest:latest
#docker push gcr.io/wdmproject23-v2/payment-rest:latest

#docker tag payment-worker gcr.io/wdmproject23-v2/payment-worker:latest
#docker push gcr.io/wdmproject23-v2/payment-worker:latest

#docker tag order-rest gcr.io/wdmproject23-v2/order-rest:latest
#docker push gcr.io/wdmproject23-v2/order-rest:latest

#docker tag order-worker gcr.io/wdmproject23-v2/order-worker:latest
#docker push gcr.io/wdmproject23-v2/order-worker:latest

cd k8s

kubectl apply -f zookeeper.yaml

sleep 15

kubectl apply -f kafka.yaml

sleep 15

#kubectl apply -f payment-db.yaml
#kubectl apply -f order-db.yaml

#sleep 15

kubectl apply -f kafka-admin.yaml

sleep 15

kubectl apply -f stock-worker.yaml
#kubectl apply -f payment-worker.yaml
#kubectl apply -f order-worker.yaml

sleep 10

kubectl apply -f stock-rest.yaml
#kubectl apply -f payment-rest.yaml
#kubectl apply -f order-rest.yaml

minikube tunnel
