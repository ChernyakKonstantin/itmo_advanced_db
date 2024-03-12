#!/bin/bash

kubectl create -f configmap.yaml
kubectl apply -f deployment-service.yaml
