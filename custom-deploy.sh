#!/usr/bin/env bash

gcloud config set project "$PROJECT_ID"

#TODO: Uncomment to create cluster
#gcloud container clusters create-auto $CLUSTER_NAME --region=europe-west4

gcloud container clusters get-credentials "$CLUSTER_NAME" --region="$REGION"

gcloud auth configure-docker

kubectl config use-context "$CONTEXT_NAME"

docker-compose build

docker tag kafka-admin gcr.io/"$PROJECT_ID"/kafka-admin:latest
docker push gcr.io/"$PROJECT_ID"/kafka-admin:latest

docker tag order-rest gcr.io/"$PROJECT_ID"/order-rest:latest
docker push gcr.io/"$PROJECT_ID"/order-rest:latest

docker tag order-worker gcr.io/"$PROJECT_ID"/order-worker:latest
docker push gcr.io/"$PROJECT_ID"/order-worker:latest

docker tag stock-rest2 gcr.io/"$PROJECT_ID"/stock-rest2
docker push gcr.io/"$PROJECT_ID"/stock-rest2

docker tag stock-worker2 gcr.io/"$PROJECT_ID"/stock-worker2
docker push gcr.io/"$PROJECT_ID"/stock-worker2

docker tag payment-rest gcr.io/"$PROJECT_ID"/payment-rest:latest
docker push gcr.io/"$PROJECT_ID"/payment-rest:latest

docker tag payment-worker gcr.io/"$PROJECT_ID"/payment-worker:latest
docker push gcr.io/"$PROJECT_ID"/payment-worker:latest


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

gcloud compute forwarding-rules list