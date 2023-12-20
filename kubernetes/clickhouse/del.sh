#!/bin/bash

kubectl delete statefulsets/clickhouse-server --namespace kchernjak-338571
kubectl delete pvc --all --namespace kchernjak-338571  
kubectl delete configmaps/clickhouse-server --namespace kchernjak-338571
kubectl delete services/clickhouse-server --namespace kchernjak-338571