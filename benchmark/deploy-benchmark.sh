gcloud config set project wdmproject23-v2
# Uncomment to create cluster
#gcloud container clusters create-auto app-cluster --region=europe-west4
gcloud container clusters get-credentials app-cluster --region=europe-west4
gcloud auth configure-docker
kubectl config use-context gke_wdmproject23-v2_europe-west4_app-cluster

cd docker-image

docker build -t locust .

docker tag locust gcr.io/wdmproject23-v2/locust:latest
docker push gcr.io/wdmproject23-v2/locust:latest

cd ../k8s

kubectl apply -f .
