#!/bin/bash

kubectl create -f lenses-deployment.yaml
kubectl apply -f lenses-service.yaml