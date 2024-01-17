import logging
import os

import clickhouse_connect

logging.basicConfig(level=logging.INFO)

sql_command_mark_existing_data_as_old = (
    "INSERT INTO TABLE sensor_storage.sensors_data_per_second (sensor_id, timestamp, measurement, n_samples, sign) "
    "SELECT sensor_id, timestamp, measurement, n_samples, -1 "
    "FROM sensor_storage.sensors_data_per_second"
)
sql_command_update_with_new_data = (
    "INSERT INTO TABLE sensor_storage.sensors_data_per_second (sensor_id, timestamp, measurement, n_samples) "
    "WITH rounded_ts_data AS ( "
    "SELECT sensor_id, toDateTime(timestamp) as timestamp, measurement "
    "FROM sensor_storage.sensors_data "
    "), "
    "aggregated_data AS ( "
    "SELECT sensor_id, timestamp, AVG(measurement) as measurement, COUNT(*) AS n_samples "
    "FROM rounded_ts_data "
    "GROUP BY sensor_id, timestamp "
    ") "
    "SELECT * FROM aggregated_data;"
)
sql_command_optimize = (
    "OPTIMIZE TABLE sensor_storage.sensors_data_per_second_local ON CLUSTER sensor_data_cluster_2S_2R"
)


if __name__ == "__main__":
    client = clickhouse_connect.get_client(
        host=os.environ["CLICKHOUSE_HOST"] if "CLICKHOUSE_HOST" in os.environ else "localhost",
        username=os.environ["CLICKHOUSE_USERNAME"] if "CLICKHOUSE_USERNAME" in os.environ else "default",
        password=os.environ["CLICKHOUSE_PASSWORD"] if "CLICKHOUSE_PASSWORD" in os.environ else "12345",
        database=os.environ["CLICKHOUSE_DATABASE"] if "CLICKHOUSE_DATABASE" in os.environ else "sensor_storage",
    )
    logging.info("Marking data as depreciated")
    summary = client.command(sql_command_mark_existing_data_as_old)

    logging.info("Aggregating and inserting new data")
    summary = client.command(sql_command_update_with_new_data)

    logging.info("Table optimization")
    summary = client.command(sql_command_optimize)

    logging.info("Finish")
