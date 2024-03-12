import logging
from datetime import datetime
from typing import Dict, Tuple

import clickhouse_connect
import pandas as pd

logging.basicConfig(level=logging.INFO)


class ClickHouseClient:
    def __init__(
        self, host: str = "127.0.0.1", username="default", password: str = "12345", database: str = "sensor_storage"
    ):
        self.client = clickhouse_connect.get_client(
            host=host,
            username=username,
            password=password,
            database=database,
        )

    def get_data(self, sensors_ids: Tuple[int], start_ts: datetime, end_ts: datetime) -> Dict[int, pd.DataFrame]:
        result = {}
        for sensor_id in sensors_ids:
            query = (
                f"SELECT timestamp, measurement FROM sensor_storage.sensors_data_per_second "
                f"WHERE sensor_id = {sensor_id} "
                f"AND (timestamp BETWEEN '{start_ts}' AND '{end_ts}') "
                f"AND sign = 1 "
                f"ORDER BY timestamp"
            )
            logging.info(f"Query: {query}")
            df = self.client.query_df(query)
            logging.info(f"Selected data: {df.shape}")
            result[sensor_id] = df
        return result

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, exc_tb):
        self.close()

    def close(self):
        self.client.close()


if __name__ == "__main__":
    with ClickHouseClient() as client:
        df = client.get_data(
            (1,), datetime.fromisoformat("2024-01-11 14:15:10"), datetime.fromisoformat("2024-01-11 15:19:12")
        )
    print(df)
