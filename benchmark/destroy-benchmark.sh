gcloud config set project wdm-benchmark

gcloud container clusters get-credentials benchmark-cluster --region=europe-west4
gcloud auth configure-docker
kubectl config use-context gke_wdm-benchmark_europe-west4_benchmark-cluster

cd k8s

kubectl delete -f .

