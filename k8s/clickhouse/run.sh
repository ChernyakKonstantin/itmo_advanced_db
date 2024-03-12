#!/bin/bash

kubectl create -f configmap.yaml
# kubectl create -f pv.yaml
kubectl apply -f statefulset-service.yaml
