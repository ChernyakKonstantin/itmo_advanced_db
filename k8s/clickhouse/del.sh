#!/bin/bash

kubectl delete statefulsets/clickhouse-server --namespace kchernjak-338571
kubectl delete pvc/clickhouse-server-storage-clickhouse-server-0 --namespace kchernjak-338571
kubectl delete pvc/clickhouse-server-storage-clickhouse-server-1 --namespace kchernjak-338571
kubectl delete pvc/clickhouse-server-storage-clickhouse-server-2 --namespace kchernjak-338571
kubectl delete pvc/clickhouse-server-storage-clickhouse-server-3 --namespace kchernjak-338571
kubectl delete configmaps/clickhouse-server --namespace kchernjak-338571
kubectl delete services/clickhouse-server-service --namespace kchernjak-338571
