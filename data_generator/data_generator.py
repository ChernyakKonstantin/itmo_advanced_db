import sched
import time
import datetime
import json
import random
from fire import Fire
import threading
import numpy as np
from kafka import KafkaProducer
from collections import defaultdict
import numpy as np
import datetime
from pprint import pprint
import random
import sched
import time
from typing import Any, Dict, List


class Sensor:
    def __init__(
        self,
        start: datetime.datetime,
        delta: datetime.timedelta = datetime.timedelta(milliseconds=1),
        failure_probability: float = 0.005
    ):
        self.delta = delta
        self.failure_probability = failure_probability
        
        self.clock = start
        self.lost_samples = []
        self.is_failure = False
        self.failure_end = None
        
    def maybe_start_failure(self):
        if not self.is_failure and random.random() < self.failure_probability:
            self.is_failure = True
            failure_duration  = random.random() * 100
            self.failure_end = self.clock + datetime.timedelta(seconds=failure_duration)
            
    def maybe_stop_failure(self):
        if self.failure_end is not None and self.failure_end <= self.clock:
            self.is_failure = False
            self.failure_end = None
    
    def __next__(self) -> List[Dict[str, Any]]:
        self.maybe_start_failure()
                
        sample = {
            "timestamp": str(self.clock),
            "measurment": random.random() * 100,
        } 
        self.clock += self.delta
        
        self.maybe_stop_failure()
        
        if self.is_failure:
            self.lost_samples.append(sample)
            raise TimeoutError
        elif len(self.lost_samples) > 0:
            response = [sample, ] + self.lost_samples
            self.lost_samples.clear()
        else:
            response = [sample, ]
        return response
            
    def __iter__(self):
        return self


class SensorAggregator:
    def __init__(self, frequency: float = 3, n_sensors: int = 10):
        """

        Parameters:
        -----------
        :param: frequency: Number of seconds between calling subscriber's method `receive` to send data.
        :type: float
        :param: n_sensors: Number of sensors to aggregate data from.
        :type: int
        """
        start = datetime.datetime.now()

        self.frequency = frequency
        self.n_sensors = n_sensors
        
        self.sensors = {f"sensor_{i}": Sensor(start) for i in range(self.n_sensors)}
        self.buffer = defaultdict(list)
    
    def poll(self):
        print("polling started")
        while True:
            for sensor_name, sensor in self.sensors.items():
                try:
                    self.buffer[sensor_name].extend(next(sensor))
                except TimeoutError:
                    pass
                
    def send_data(self):
        # TODO: is this solution good? I make `self.buffer` pointing to another memory area.
        to_send = self.buffer
        # print(id(to_send), id(self.buffer))
        self.buffer = defaultdict(list)
        # print(id(to_send), id(self.buffer))
        
        pprint({k: len(v) for k, v in to_send.items()})
        print()

    
    def run(self):
        polling_thread = threading.Thread(target=self.poll, daemon=True)
        polling_thread.start()

        sheduler = sched.scheduler(time.time, time.sleep)
        while True:
            sheduler.enter(self.frequency, 1, self.send_data)
            sheduler.run()


def main(frequency: int = None):
    if frequency is None:
        aggregator = SensorAggregator()
    else:
        aggregator = SensorAggregator(frequency)
    aggregator.run()


if __name__ == "__main__":
    Fire(main)
