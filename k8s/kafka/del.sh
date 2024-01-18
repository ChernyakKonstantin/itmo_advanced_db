#!/bin/bash

kubectl delete statefulsets/kafka --namespace kchernjak-338571
kubectl delete services/kafka-service --namespace kchernjak-338571
kubectl delete pvc/logs-kafka-0 --namespace kchernjak-338571
# kubectl delete pvc/logs-kafka-1 --namespace kchernjak-338571
# kubectl delete pvc/logs-kafka-2 --namespace kchernjak-338571
