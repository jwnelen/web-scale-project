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

docker tag order-rest-final gcr.io/"$PROJECT_ID"/order-rest-final
docker push gcr.io/"$PROJECT_ID"/order-rest-final

docker tag order-worker-final gcr.io/"$PROJECT_ID"/order-worker-final
docker push gcr.io/"$PROJECT_ID"/order-worker-final

docker tag stock-rest-final gcr.io/"$PROJECT_ID"/stock-rest-final
docker push gcr.io/"$PROJECT_ID"/stock-rest-final

docker tag stock-worker-final gcr.io/"$PROJECT_ID"/stock-worker-final
docker push gcr.io/"$PROJECT_ID"/stock-worker-final

docker tag payment-rest-final gcr.io/"$PROJECT_ID"/payment-rest-final
docker push gcr.io/"$PROJECT_ID"/payment-rest-final

docker tag payment-worker-final gcr.io/"$PROJECT_ID"/payment-worker-final
docker push gcr.io/"$PROJECT_ID"/payment-worker-final


cd k8s

kubectl apply -f config-map.yaml

sleep 5

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
