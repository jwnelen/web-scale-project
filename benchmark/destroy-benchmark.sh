gcloud config set project wdmproject23-v2
# Uncomment to create cluster
#gcloud container clusters create-auto app-cluster --region=europe-west4
gcloud container clusters get-credentials app-cluster --region=europe-west4
gcloud auth configure-docker
kubectl config use-context gke_wdmproject23-v2_europe-west4_app-cluster

cd k8s

kubectl delete -f .

