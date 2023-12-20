#!/bin/bash

kubectl create -f clickhouse-server-configmap.yaml
kubectl apply -f clickhouse-server-statefulset.yaml
kubectl apply -f clickhouse-server-service.yaml