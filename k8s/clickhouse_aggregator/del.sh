#!/bin/bash

kubectl delete deployments/aggregate-data-job --namespace kchernjak-338571
kubectl delete services/aggregate-data-job-service --namespace kchernjak-338571
