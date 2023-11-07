import time
import datetime

for _ in range(1000):
    print(datetime.datetime.fromtimestamp(time.time()))
    
    
    
echo '{"name":"load-kafka-config", "config":{"connector.class":"FileStreamSource", "file":"config/server.properties","topic":"kafka-config-topic"}}' | curl -X POST -d @- http://localhost:8083/connectors --header "contentType:application/json"


bin/kafka-console-consumer.sh --new-consumer --bootstrap-server=localhost:9092 --topic kafka-config-topic --from-beginning