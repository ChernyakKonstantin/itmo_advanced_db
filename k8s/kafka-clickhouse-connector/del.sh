#!/bin/bash

kubectl delete statefulsets/kafka-connect --namespace kchernjak-338571
kubectl delete services/kafka-connect-service --namespace kchernjak-338571
# kubectl delete pvc/logs-kafka-connect-0 --namespace kchernjak-338571
# kubectl delete pvc/logs-kafka-connect-1 --namespace kchernjak-338571
# kubectl delete pvc/logs-kafka-connect-2 --namespace kchernjak-338571
