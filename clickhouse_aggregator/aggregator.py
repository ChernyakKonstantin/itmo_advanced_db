import logging
import os
import datetime
import clickhouse_connect

logging.basicConfig(level=logging.INFO)


if __name__ == "__main__":
    client = clickhouse_connect.get_client(
        host=os.environ["CLICKHOUSE_HOST"] if "CLICKHOUSE_HOST" in os.environ else "localhost",
        username=os.environ["CLICKHOUSE_USERNAME"] if "CLICKHOUSE_USERNAME" in os.environ else "default",
        password=os.environ["CLICKHOUSE_PASSWORD"] if "CLICKHOUSE_PASSWORD" in os.environ else "12345",
        database=os.environ["CLICKHOUSE_DATABASE"] if "CLICKHOUSE_DATABASE" in os.environ else "sensor_storage",
    )
    today_start = datetime.datetime.now().date().strftime("%F %T.%f")

    sql_command_mark_existing_data_as_old = (
        f"INSERT INTO TABLE sensor_storage.sensors_data_per_second (sensor_id, timestamp, measurement, n_samples, sign) "
        f"SELECT sensor_id, timestamp, measurement, n_samples, -1 "
        f"FROM sensor_storage.sensors_data_per_second "
        f"WHERE timestamp >= {today_start}"
    )
    sql_command_update_with_new_data = (
        f"INSERT INTO TABLE sensor_storage.sensors_data_per_second (sensor_id, timestamp, measurement, n_samples) "
        f"WITH rounded_ts_data AS ( "
        f"   SELECT sensor_id, toDateTime(timestamp) as timestamp, measurement "
        f"   FROM sensor_storage.sensors_data "
        f"   WHERE timestamp >= {today_start}"
        f"), "
        f"aggregated_data AS ( "
        f"   SELECT sensor_id, timestamp, AVG(measurement) as measurement, COUNT(*) AS n_samples "
        f"   FROM rounded_ts_data "
        f"   GROUP BY sensor_id, timestamp "
        f") "
        f"SELECT * FROM aggregated_data;"
    )
    sql_command_optimize = (
        "OPTIMIZE TABLE sensor_storage.sensors_data_per_second_local ON CLUSTER sensor_data_cluster_2S_2R"
    )

    logging.info("Marking data as depreciated")
    summary = client.command(sql_command_mark_existing_data_as_old)

    logging.info("Aggregating and inserting new data")
    summary = client.command(sql_command_update_with_new_data)

    logging.info("Table optimization")
    summary = client.command(sql_command_optimize)

    logging.info("Finish")
