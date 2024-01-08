#!/bin/bash

kubectl create -f configmap.yaml
kubectl apply -f statefulset-service.yaml
