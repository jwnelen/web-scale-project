#!/usr/bin/env bash

gcloud config set project wdmproject23

gcloud container clusters create-auto app-cluster --region=europe-west4

gcloud container clusters get-credentials app-cluster --region=europe-west4

gcloud auth configure-docker

kubectl config use-context gke_wdmproject23_europe-west4_app-cluster

docker-compose build

docker tag order gcr.io/wdmproject23/order
docker push gcr.io/wdmproject23/order

docker tag stock gcr.io/wdmproject23/stock
docker push gcr.io/wdmproject23/stock

docker tag user gcr.io/wdmproject23/user
docker push gcr.io/wdmproject23/user

helm repo add bitnami https://charts.bitnami.com/bitnami
helm repo add ingress-nginx https://kubernetes.github.io/ingress-nginx

helm repo update

helm install -f helm-config/redis-helm-values.yaml redis bitnami/redis
helm install -f helm-config/nginx-helm-values.yaml nginx ingress-nginx/ingress-nginx

cd k8s-gcloud
kubectl apply -f .