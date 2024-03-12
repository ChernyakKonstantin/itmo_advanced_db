import datetime
import json
import logging
import os
import time
from typing import Optional, Tuple

import clickhouse_connect
import numpy as np
from confluent_kafka import Producer

logging.basicConfig(level=logging.INFO)


def timestamp2datetime64(timestamp: float) -> datetime.datetime:
    return datetime.datetime.fromtimestamp(timestamp)


class ClickhouseSinkConnector:
    def __init__(self, clickhouse_servers: str):
        self.client = clickhouse_connect.get_client(
            host=clickhouse_servers,
            username="default",
            password="12345",
            database="sensor_storage",
        )
        self.table_name = "sensors_data"
        self.column_names = [
            "timestamp",
            "sensor_id",
            "measurement",
        ]
        self.column_types = [
            clickhouse_connect.datatypes.temporal.DateTime64,
            clickhouse_connect.datatypes.numeric.UInt32,
            clickhouse_connect.datatypes.numeric.Float32,
        ]
        logging.info(f"Clickhouse bootstrap servers: {clickhouse_servers}")

    def send_data(self, timestamp: np.ndarray, sensor_id: np.ndarray, measurement: np.ndarray):
        self.client.insert(
            table=self.table_name,
            data=[timestamp, sensor_id, [timestamp2datetime64(m) for m in measurement]],
            column_names=self.column_names,
            column_types=self.column_types,
            column_oriented=True,
        )
        logging.info(f"Sent samples: {len(timestamp)}")


class KafkaSinkConnector:
    def __init__(self, kafka_servers: str):
        producer_config = {
            "bootstrap.servers": kafka_servers,
            "queue.buffering.max.messages": 2_000_000,
            "connections.max.idle.ms": 540_000,
            "retries": 1,
        }
        self.kafka_producer = Producer(producer_config)
        self.topic_name = "sensors_data"
        logging.info(f"Kafka bootstrap servers: {kafka_servers}")

    def send_data(self, timestamp: np.ndarray, sensor_id: np.ndarray, measurement: np.ndarray):
        records = []
        for ts, s_id, meas in zip(timestamp, sensor_id, measurement):
            record = {"timestamp": timestamp2datetime64(ts).strftime("%F %T.%f"), "sensor_id": int(s_id), "measurement": meas}
            record = json.dumps(record).encode(encoding="ascii")
            records.append(record)
        for record in records:
            self.kafka_producer.produce(self.topic_name, record, partition=0)
        self.kafka_producer.flush()
        logging.info(f"Sent samples: {len(timestamp)}")


class SensorAggregator:
    def __init__(
        self,
        sink_connector,
        frequency: float = 3,
        n_sensors: int = 5,
        failure_rate: Optional[float] = 0.05,
        response_rate: Optional[float] = 0.8,
    ):
        """

        Parameters:
        -----------
        :param: sink_connector: Kafka Producer or Clickhouse sink connector
        :param: frequency: Number of seconds between calling subscriber's method `receive` to send data.
        :type: float
        :param: n_sensors: Number of sensors to aggregate data from.
        :type: int
        :param: failure_rate: Probablilty for message to be delayed.
        :type: float
        :param: response_rate: Probablilty for delayed message to be sent.
        :type: float
        """
        logging.info(f"Number os sensors: {n_sensors}")
        logging.info(f"Aggregating duration: {frequency}")
        logging.info(f"Failure rate: {failure_rate}")
        logging.info(f"Response rate: {response_rate}")

        self.sink_connector = sink_connector
        self.start = datetime.datetime.now()

        self.frequency = frequency
        self.n_sensors = n_sensors
        self.failure_rate = failure_rate
        self.response_rate = response_rate
        self.n_samples = int(frequency * 1e3)

        # Storage of delayed data
        self.send_later_timestamp = np.array([])
        self.send_later_sensor_id = np.array([])
        self.send_later_data = np.array([])
        logging.info("Started")

    def generate_data(self) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        # Generate new data
        # 0-axis is sensor_id. 1-axis is time axis.
        stop = self.start + datetime.timedelta(seconds=1)
        timestamp = np.linspace(self.start.timestamp(), stop.timestamp(), self.n_samples)
        timestamp = np.repeat(timestamp.reshape(1, -1), self.n_sensors, axis=0)
        sensor_id = np.arange(0, self.n_sensors)
        sensor_id = np.repeat(sensor_id.reshape(-1, 1), self.n_samples, axis=1)
        data = np.random.rand(self.n_sensors, self.n_samples)
        self.start = stop
        return timestamp, sensor_id, data

    def get_masks(self) -> Tuple[np.ndarray, np.ndarray]:
        # Create mask to select current data to be sent
        mask = np.random.rand(self.n_sensors, self.n_samples)
        mask = mask > self.failure_rate

        # Create mask to select delayed data to be sent
        delayed_mask = np.random.rand(*self.send_later_timestamp.shape)
        delayed_mask = delayed_mask < self.response_rate
        return mask, delayed_mask

    def get_data(self) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        timestamp, sensor_id, data = self.generate_data()
        mask, delayed_mask = self.get_masks()

        # Select delayed data to be sent
        delayed_timestamp = self.send_later_timestamp[delayed_mask]
        delayed_sensor_id = self.send_later_sensor_id[delayed_mask]
        delayed_data = self.send_later_data[delayed_mask]

        # Update remained delayed data to be sent later
        self.send_later_timestamp = self.send_later_timestamp[~delayed_mask]
        self.send_later_sensor_id = self.send_later_sensor_id[~delayed_mask]
        self.send_later_data = self.send_later_data[~delayed_mask]

        # Select data to be sent
        send_timestamp = timestamp[mask]
        send_sensor_id = sensor_id[mask]
        send_data = data[mask]

        # Append new delayed data
        self.send_later_timestamp = np.hstack([self.send_later_timestamp, timestamp[~mask]])
        self.send_later_sensor_id = np.hstack([self.send_later_sensor_id, sensor_id[~mask]])
        self.send_later_data = np.hstack([self.send_later_data, data[~mask]])

        # Add delayed data to data to be sent
        send_timestamp = np.hstack([send_timestamp, delayed_timestamp])
        send_sensor_id = np.hstack([send_sensor_id, delayed_sensor_id])
        send_data = np.hstack([send_data, delayed_data])
        return send_timestamp, send_sensor_id, send_data

    def run(self):
        while True:
            on_iteration_start_ts = time.time()
            timestamp, sensor_id, data = self.get_data()  # It takes ~ 0.05 seconds for 1k sensors of 1kHz.
            self.sink_connector.send_data(timestamp, sensor_id, data)
            on_iteration_end_ts = time.time()
            iteration_duration = on_iteration_end_ts - on_iteration_start_ts
            logging.info(f"Iteration duration: {iteration_duration}")
            remained_time = self.frequency - iteration_duration
            if remained_time > 0:
                time.sleep(remained_time)


def main():
    try:
        kafka_brokers = os.environ["KAFKA_BROKERS"]
    except KeyError:
        kafka_brokers = None
    try:
        clickhouse_servers = os.environ["CLICKHOUSE_SERVERS"]
    except KeyError:
        clickhouse_servers = None

    aggregation_frequency = float(os.environ["AGGREGATION_FREQUENCY"])
    n_sensors = int(os.environ["N_SENSORS"])
    failure_rate = float(os.environ["FAILURE_RATE"])
    response_rate = float(os.environ["RESPONSE_RATE"])

    if kafka_brokers is not None:
        sink_connector = KafkaSinkConnector(kafka_brokers)
    elif clickhouse_servers is not None:
        sink_connector = ClickhouseSinkConnector(clickhouse_servers)
    else:
        raise RuntimeError("No sink connector available")

    aggregator = SensorAggregator(
        sink_connector,
        aggregation_frequency,
        n_sensors,
        failure_rate,
        response_rate,
    )
    aggregator.run()


if __name__ == "__main__":
    main()
