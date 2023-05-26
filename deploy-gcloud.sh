#!/usr/bin/env bash

gcloud config set project wdmproject23-v2

# Uncomment to create cluster
#gcloud container clusters create-auto app-cluster --region=europe-west4

gcloud container clusters get-credentials app-cluster --region=europe-west4

gcloud auth configure-docker

kubectl config use-context gke_wdmproject23-v2_europe-west4_app-cluster

docker-compose build

docker tag order gcr.io/wdmproject23-v2/order:latest
docker push gcr.io/wdmproject23-v2/order:latest

docker tag stock gcr.io/wdmproject23-v2/stock:latest
docker push gcr.io/wdmproject23-v2/stock:latest

docker tag user gcr.io/wdmproject23-v2/user:latest
docker push gcr.io/wdmproject23-v2/user:latest

#helm repo add ingress-nginx https://kubernetes.github.io/ingress-nginx
#
#helm repo update
#
#helm install -f helm-config/nginx-helm-values.yaml nginx ingress-nginx/ingress-nginx

cd k8s-gcloud
kubectl apply -f order-db.yaml
kubectl apply -f stock-db.yaml
kubectl apply -f user-db.yaml

sleep 10

kubectl apply -f order-app.yaml
kubectl apply -f stock-app.yaml
kubectl apply -f user-app.yaml

sleep 20
kubectl apply -f ingress-service.yaml

gcloud compute forwarding-rules list
