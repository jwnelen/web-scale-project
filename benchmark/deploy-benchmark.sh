gcloud config set project wdm-benchmark
# Uncomment to create cluster
gcloud container clusters create-auto benchmark-cluster --region=europe-west4
gcloud container clusters get-credentials benchmark-cluster --region=europe-west4
gcloud auth configure-docker
kubectl config use-context gke_wdm-benchmark_europe-west4_benchmark-cluster

cd docker-image

docker build -t locust .

docker tag locust gcr.io/wdm-benchmark/locust:latest
docker push gcr.io/wdm-benchmark/locust:latest

cd ../k8s

kubectl apply -f .
