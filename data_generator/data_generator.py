import sched
import time
import datetime
import random
from fire import Fire
import threading

class Sensor:
    def __init__(self, frequency: float = 1e-3):
        """
        
        Parameters:
        -----------
        :param: frequency: Number of seconds between answering to request.
        :type: float
        """
        self.frequency = frequency
        self.sheduler = sched.scheduler(time.time, time.sleep)

    def generate_data(self):
        return (
            datetime.datetime.fromtimestamp(time.time()), 
            random.random(),
        )
    
    def get_data(self):
        # TODO: fix
        # time.sleep(self.frequency)
        return self.generate_data()

        
class SensorAggregator:
    def __init__(self, frequency: float = 3, n_sensors: int = 1000):
        """

        Parameters:
        -----------
        :param: frequency: Number of seconds between calling subscriber's method `receive` to send data.
        :type: float
        :param: n_sensors: Number of sensors to aggregate data from.
        :type: int
        """

        self.frequency = frequency
        self.n_sensors = n_sensors
        self.sensors = [Sensor(self) for _ in range(self.n_sensors)]        
        self.buffer = []
        self.lock = threading.Lock()


    def poll(self):
        print("polling started")
        while True:
            for sensor in self.sensors:
                self.buffer.append(sensor.get_data())

    def send_data(self):
        self.lock.acquire()
        print(len(self.buffer))
        self.buffer.clear()
        self.lock.release()
    
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
