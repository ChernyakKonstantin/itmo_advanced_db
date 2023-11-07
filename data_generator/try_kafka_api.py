from kafka import KafkaProducer
from kafka.errors import KafkaError
import json

def on_send_success(record_metadata):
    print(record_metadata.topic)
    print(record_metadata.partition)
    print(record_metadata.offset)

def on_send_error(excp):
    print('I am an errback', exc_info=excp)

# produce json messages
producer = KafkaProducer(
    bootstrap_servers=['kafka:9092'],  # TODO: How should I dynamically set address if I have several kafka brokers?
    value_serializer=lambda x: json.dumps(x).encode('ascii'),
    retries=5,
)

future = producer.send(
    "sensor_1",
    {"record_id": 2, "timestamp": "2023-11-06 10:30:00", "measurement": 23.45},
)
# print(future)
producer.flush()

# datas = [
#     {
#         "timestamp": 190,
#         "measurment": 0.17,
#     },
#     {
#         "timestamp": 191,
#         "measurment": 0.18,
#     },
# ]

# topics = ["sensor_0", "sensor_1"]

# for topic, data in zip(topics, datas):
#     producer.send('json-topic', {'key': 'value'}).add_callback(on_send_success).add_errback(on_send_error)

# producer.flush()

