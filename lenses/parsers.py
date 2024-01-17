import re
from datetime import datetime, timedelta
from typing import Tuple


def parse_sensors(sensors: str) -> Tuple[int]:
    sensors = re.findall("\d+", sensors)
    return tuple(map(int, sensors))


def is_ts(ts: str) -> bool:
    return re.match("\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}", ts) is not None


def parse_ts(ts: str) -> datetime:
    return datetime.fromisoformat(ts)


def parse_duration(duration: str) -> timedelta:
    seconds = re.findall("\d+s", duration)
    if len(seconds) > 0:
        return timedelta(seconds=int(seconds[0][:-1]))
    minutes = re.findall("\d+m", duration)
    if len(minutes) > 0:
        return timedelta(minutes=int(minutes[0][:-1]))
    hours = re.findall("\d+h", duration)
    if len(hours) > 0:
        return timedelta(hours=int(hours[0][:-1]))
