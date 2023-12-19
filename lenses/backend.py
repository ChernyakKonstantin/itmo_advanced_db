import io
from typing import Union

from clickhouse_client import ClickHouseClient
from drawer import PngDrawer
from error_codes import BackendErrors
from parsers import is_ts, parse_duration, parse_sensors, parse_ts


class Backend:
    def __init__(self):
        self.drawer = PngDrawer()

    def get_result(self, sensors: str, start: str, end_or_duration: str) -> Union[io.BytesIO, BackendErrors]:
        try:
            sensors = parse_sensors(sensors)
        except Exception as e:
            print(e)  # TODO: Move to logging
            return BackendErrors.WRONG_SENSOR_LIST
        try:
            start = parse_ts(start)
        except Exception as e:
            print(e)  # TODO: Move to logging
            return BackendErrors.WRONG_START_TIMESTAMP
        try:
            if is_ts(end_or_duration):
                end = parse_ts(end_or_duration)
            else:
                duration = parse_duration(end_or_duration)
                end = parse_ts(start) + duration
        except Exception as e:
            print(e)  # TODO: Move to logging
            return BackendErrors.WRONG_END_TIMESTAMP
        with ClickHouseClient() as clickhouse_client:  # TODO: Set correct data
            sensor_data = clickhouse_client.get_data(sensors, start, end)
        if len(sensor_data) == 0:
            return BackendErrors.NO_DATA
        else:
            return self.drawer.draw(sensor_data)
