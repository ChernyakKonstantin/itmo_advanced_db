#!/bin/bash

kubectl delete deployments/sensors --namespace kchernjak-338571
kubectl delete services/sensors-service --namespace kchernjak-338571
kubectl delete configmaps/clickhouse-sink-connector-runner --namespace kchernjak-338571
