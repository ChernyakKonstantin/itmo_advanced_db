import datetime
import json
import logging
import os
import random
import time
from typing import List, Optional, Tuple

import numpy as np
from kafka import KafkaProducer

logging.basicConfig(level=logging.INFO)


class SensorAggregator:
    def __init__(
        self,
        kafka_servers: List[str],
        frequency: float = 3,
        n_sensors: int = 5,
        topic_name: Optional[str] = "sensors_data",
        failure_rate: Optional[float] = 0.05,
        response_rate: Optional[float] = 0.8,
    ):
        """

        Parameters:
        -----------
        :param: frequency: Number of seconds between calling subscriber's method `receive` to send data.
        :type: float
        :param: n_sensors: Number of sensors to aggregate data from.
        :type: int
        :param: topic_name: Kafka topic name to send data to.
        :type: str
        :param: failure_rate: Probablilty for message to be delayed.
        :type: float
        :param: response_rate: Probablilty for delayed message to be sent.
        :type: float
        """
        logging.info(f"Kafka bootstrap servers: {kafka_servers}")
        logging.info(f"Number os sensors: {n_sensors}")
        logging.info(f"Aggregating duration: {frequency}")
        logging.info(f"Data topic: {topic_name}")
        logging.info(f"Failure rate: {failure_rate}")
        logging.info(f"Response rate: {response_rate}")

        self.start = datetime.datetime.now()

        self.frequency = frequency
        self.n_sensors = n_sensors
        self.topic_name = topic_name
        self.failure_rate = failure_rate
        self.response_rate = response_rate
        self.n_samples = int(frequency * 1e3)

        # Storage of delayed data
        self.send_later_timestamp = np.array([])
        self.send_later_sensor_id = np.array([])
        self.send_later_data = np.array([])

        self.kafka_producer = KafkaProducer(
            bootstrap_servers=kafka_servers,
            value_serializer=lambda x: json.dumps(x).encode("ascii"),
            acks=1,
        )
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

    def send_data(self, timestamp: np.ndarray, sensor_id: np.ndarray, data: np.ndarray) -> None:
        for ts, s_id, d in zip(timestamp, sensor_id, data):
            record = {"timestamp": str(datetime.datetime.fromtimestamp(ts)), "sensor_id": int(s_id), "measurement": d}
            self.kafka_producer.send(self.topic_name, record)
        logging.info(f"Sent samples: {len(timestamp)}")

    def run(self):
        while True:
            on_iteration_start_ts = time.time()
            timestamp, sensor_id, data = self.get_data()  # It takes ~ 0.05 seconds for 1k sensors of 1kHz.
            self.send_data(timestamp, sensor_id, data)
            on_iteration_end_ts = time.time()
            iteration_duration = on_iteration_end_ts - on_iteration_start_ts
            logging.info(f"Iteration duration: {iteration_duration}")
            remained_time = self.frequency - iteration_duration
            if remained_time > 0:
                time.sleep(remained_time)


def main():
    kafka_brokers = os.environ["KAFKA_BROKERS"].split(",")
    aggregation_frequency = float(os.environ["AGGREGATION_FREQUENCY"])
    n_sensors = int(os.environ["N_SENSORS"])
    topic_name = os.environ["TOPIC_NAME"]
    failure_rate = float(os.environ["FAILURE_RATE"])
    response_rate = float(os.environ["RESPONSE_RATE"])
    aggregator = SensorAggregator(kafka_brokers, aggregation_frequency, n_sensors, topic_name, failure_rate, response_rate)
    aggregator.run()


if __name__ == "__main__":
    main()
