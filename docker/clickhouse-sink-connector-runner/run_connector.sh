#!bin/sh

echo 'Install curl'
apk --update add curl

echo

echo 'Run clickhouse sink connector'
curl -X PUT -H "content-Type:application/json" http://$KAFKA_CONNECT/connectors/clickhouse-connect/config -d \
'{
    "connector.class": "com.clickhouse.kafka.connect.ClickHouseSinkConnector",
    "ssl": "false",
    "tasks.max": "1",
    "value.converter.schemas.enable": "false",
    "exactlyOnce": "true",
    "database": "sensor_storage",
    "hostname": "'$CLICKHOUSE_HOST'",
    "port": "8123",
    "username": "default",
    "password": "12345",
    "topics": "sensors_data",
    "consumer.max.poll.records":"10000"
}'
