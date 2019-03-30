#!/bin/bash

kubectl create -f ./spark-master-deployment.yaml
kubectl create -f ./spark-master-service.yaml

sleep 10

kubectl create -f ./spark-worker-deployment.yaml
kubectl apply -f ./minikube-ingress.yaml
