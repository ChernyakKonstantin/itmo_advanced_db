#!/bin/bash

minikube start --cpus=no-limit --driver=docker --memory=no-limit
minikube addons enable metrics-server
minikube dashboard