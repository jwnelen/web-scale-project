#!/usr/bin/env bash

gcloud config set project "$PROJECT_ID"

#TODO: Uncomment to create cluster
#gcloud container clusters create-auto $CLUSTER_NAME --region=europe-west4

gcloud container clusters get-credentials "$CLUSTER_NAME" --region="$REGION"

gcloud auth configure-docker

kubectl config use-context "$CONTEXT_NAME"

docker-compose build

docker tag kafka-admin gcr.io/"$PROJECT_ID"/kafka-admin
docker push gcr.io/"$PROJECT_ID"/kafka-admin

docker tag order-rest2 gcr.io/"$PROJECT_ID"/order-rest2
docker push gcr.io/"$PROJECT_ID"/order-rest2

docker tag order-worker2 gcr.io/"$PROJECT_ID"/order-worker2
docker push gcr.io/"$PROJECT_ID"/order-worker2

docker tag stock-rest2 gcr.io/"$PROJECT_ID"/stock-rest2
docker push gcr.io/"$PROJECT_ID"/stock-rest2

docker tag stock-worker2 gcr.io/"$PROJECT_ID"/stock-worker2
docker push gcr.io/"$PROJECT_ID"/stock-worker2

docker tag payment-rest3 gcr.io/"$PROJECT_ID"/payment-rest3
docker push gcr.io/"$PROJECT_ID"/payment-rest3

docker tag payment-worker2 gcr.io/"$PROJECT_ID"/payment-worker2
docker push gcr.io/"$PROJECT_ID"/payment-worker2


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
