To setup spark and kubernetes interface, please follow the below steps:
1) Setup Minikube. To do so, download and install a hypervisor (virtualbox in Ubuntu 18.04 was used in this project). Then install kubectl and Minikube, (Follow https://kubernetes.io/docs/tasks/tools/install-minikube/).
2) Start the cluster: minikube start --memory 8192 --cpus 4
3) Build the docker image: eval $(minikube docker-env), $ docker build -t spark-hadoop:2.2.1 .
4) Create the Spark master deployment: $ kubectl create -f ./kubernetes/spark-master-deployment.yaml
5) Start the Spark services: kubectl create -f ./kubernetes/spark-master-service.yaml
6) Create Spark worker deployment: kubectl create -f ./kubernetes/spark-worker-deployment.yaml
7) Enable the ingress addon:  minikube addons enable ingress
8) Create the ingress object: kubectl apply -f ./kubernetes/minikube-ingress.yaml
9) Update to route requests from defined host to minikube: $ echo "$(minikube ip) spark-kubernetes" | sudo tee -a /etc/hosts

Based off of: https://testdriven.io/blog/deploying-spark-on-kubernetes/
