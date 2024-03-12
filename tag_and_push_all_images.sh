#!/bin/bash

docker image tag busybox:1.33.0 node03.st:5000/kainrehck_busybox:latest
docker image tag clickhouse/clickhouse-server:23.11.2.11 node03.st:5000/kainrehck/clickhouse:latest
docker image tag kainrehck/advanced_db:clickhouse_aggregator_x86 node03.st:5000/kainrehck/clickhouse_aggregator_x86:latest
docker image tag bitnami/kafka:latest node03.st:5000/kainrehck/kafka:latest
docker image tag kainrehck/advanced_db:kafka-connect_x86 node03.st:5000/kainrehck/kafka-connect_x86:latest
docker image tag kainrehck/advanced_db:lenses_x86 node03.st:5000/kainrehck/lenses_x86:latest
docker image tag kainrehck/advanced_db:sensor_data_generator_x86 node03.st:5000/kainrehck/sensor_data_generator_x86:latest
docker image tag confluentinc/cp-zookeeper:latest node03.st:5000/kainrehck/cp-zookeeper:latest
docker image tag kainrehck/advanced_db:clickhouse_connector_runner_x86 node03.st:5000/kainrehck/clickhouse_connector_runner_x86:latest

docker push node03.st:5000/kainrehck_busybox:latest
docker push node03.st:5000/kainrehck/clickhouse:latest
docker push node03.st:5000/kainrehck/clickhouse_aggregator_x86:latest
docker push node03.st:5000/kainrehck/kafka:latest
docker push node03.st:5000/kainrehck/kafka-connect_x86:latest
docker push node03.st:5000/kainrehck/lenses_x86:latest
docker push node03.st:5000/kainrehck/sensor_data_generator_x86:latest
docker push node03.st:5000/kainrehck/cp-zookeeper:latest
docker push node03.st:5000/kainrehck/clickhouse_connector_runner_x86:latest
 