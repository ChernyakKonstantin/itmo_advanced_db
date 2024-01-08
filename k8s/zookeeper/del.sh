#!/bin/bash

kubectl delete statefulsets/zookeeper --namespace kchernjak-338571
kubectl delete pvc/datadir-zookeeper-0 --namespace kchernjak-338571
kubectl delete pvc/datadir-zookeeper-1 --namespace kchernjak-338571
kubectl delete pvc/datadir-zookeeper-2 --namespace kchernjak-338571
kubectl delete services/zookeeper-service  --namespace kchernjak-338571
