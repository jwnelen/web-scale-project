# Web-scale Data Management Project

### Group Info
**Group 3:**
1. Remy Duijsens, 
2. Jeroen Nelen, 
3. Raphael Frühwirth


### Project structure
* `/backend`\
    This created the connectors that are being used by Kafka. It also contains the logic for the Kafka consumers and producers.
    
* `/kafka-admin`\
    The admin for the Kafka server. This is used for the topic creation.

* `/k8s`\
    Folder containing the kubernetes deployments, apps and services for the ingress, order, payment and stock services.

* `/k8s/dev`\
    This is the file that contains the configmap. These are values that are being used within the k8s cluster.
    These should be updated when the cluster is being deployed.
    
* `/{order, payment, stock}-rest`\
    This is the REST API for the order, payment and stock services. They are responsible for handling the incoming requests. 
    This is done by a FASTAPI server.
    
* `/{order, payment, stock}-worker`\
    These are the workers, that connect to Spanner. They will return the requested value back to the REST API of that service.

* `/test`\
    Folder containing some basic correctness tests for the entire system.

### Database: Google Spanner
For the database, we have implemented Spanner. This is a distributed database that is being managed by Google.

## deployment

### Deployment types:

#### docker-compose (local development)

After coding the REST endpoint logic run `docker-compose up --build` in the base folder to test if your logic is correct
(you can use the provided tests in the `\test` folder and change them as you wish). 

***Requirements:*** You need to have docker and docker-compose installed on your machine.

#### minikube (local k8s cluster)


#### kubernetes cluster (managed k8s cluster in the cloud)
Our deployment is done by a kubernetes cluster, that can connect to Google Spanner. Other k8s clusters can be used, but GCP is the easiest.
For this, create an account on GCP and create a project.

***Requirements:*** 
1. You need to have access to kubectl of a k8s cluster. 
2. Your docker deamon needs to run.
3. If you are indeed using the gcloud kubectl, make sure you have the right access to the cluster in your local terminal.

If you have done all the steps from below, you can run the `custom-deploy.sh` script. 
This will deploy the entire system to the k8s cluster.

#### ~~docker-compose (not working anymore)~~
Docker compose cannot be used anymore. The docker compose fill is still being used to build all images.

### How to Deploy
For deployment, a few things need to be done in order to get the system up and running.

### 1. Make sure you have the right access to Spanner
Make sure you have the right access to Spanner. For this, you need to have a service account with the right permissions.
If you are using **minikube**, you need to have a json file with the credentials in your home folder. For this, have a key jsonfile ready.
Call this file `keyfile.json` and place it in your home folder. This will be mounted to the container and used for authentication.
In **GCP Kubernetes**, it is managed by Google.

### 2. Make sure you have setup the resource limits correctly for your specific k8s cluster
Make sure you have setup the resource limits correctly for your specific k8s cluster if you are running it locally. 
Your computer might not be able to handle the default values.

### 3. Setup the configmap
Make sure you have setup the configmap correctly. This is done by the `config-map.yaml` file in the `k8s/dev` folder.

### 4. Export the right variables
Then you can use the `custom-deploy.sh` command. But make sure to update the following values:
- `export CLUSTER_NAME=app-cluster`
- `export PROJECT_ID=app-project`
- `export REGION=europe-west4`
- `export CONTEXT_NAME=gke_${PROJECT_ID}_${REGION}_${CLUSTER_NAME}` (or change this to where your images are stored)

These values will be used in the `custom-deploy.sh`

### 5. Have a place for the docker images
Make sure you have a place for the docker images. This can be done by a docker registry or by a local docker registry.
This is defined in the `deploy.sh`, so remember to update those values.

