CREATE DATABASE IF NOT EXISTS sensor_storage
ON CLUSTER sensor_data_cluster_2S_2R;

-- Create local table
CREATE TABLE IF NOT EXISTS sensor_storage.sensors_data_local
ON CLUSTER sensor_data_cluster_2S_2R
(
    sensor_id UInt32,
    timestamp DateTime64,
    measurement Float32
)
ENGINE = ReplicatedMergeTree('/clickhouse/tables/{shard}/sensors_data_local', '{replica}')
ORDER BY (sensor_id, timestamp);

-- Create distributed table
CREATE TABLE IF NOT EXISTS sensor_storage.sensors_data
ON CLUSTER sensor_data_cluster_2S_2R
AS sensor_storage.sensors_data_local
ENGINE = Distributed(sensor_data_cluster_2S_2R, sensor_storage, sensors_data_local, xxHash64(sensor_id));

-- Create materialized view with pre-aggregated per sensor measurement per second.
CREATE MATERIALIZED VIEW sensor_storage.average_measurement_per_second_local
ON CLUSTER sensor_data_cluster_2S_2R
-- Data is not shown. Need to test without replication.
ENGINE = ReplicatedAggregatingMergeTree('/clickhouse/tables/{shard}/average_measurement_per_second_local', '{replica}')
ORDER BY (sensor_id, timestamp) AS
WITH numbered_rows AS (
    SELECT
    sensor_id, timestamp, measurement, ROW_NUMBER() OVER (PARTITION BY sensor_id ORDER BY timestamp) AS row_num
    FROM sensor_storage.sensors_data_local
),
aggregated_data AS (
    SELECT sensor_id, MIN(timestamp) AS timestamp, AVG(measurement) AS measurement, FLOOR((row_num - 1) / 1000) AS group_id, COUNT(*) AS n_steps
    FROM numbered_rows
    GROUP BY sensor_id, group_id
)
SELECT sensor_id, timestamp, measurement
FROM aggregated_data
WHERE n_steps = 1000
ORDER BY sensor_id, timestamp;

-- Make materialized view distributed
CREATE TABLE sensor_storage.average_measurement_per_second
ON CLUSTER sensor_data_cluster_2S_2R
AS sensor_storage.average_measurement_per_second_local
ENGINE = Distributed(
    sensor_data_cluster_2S_2R,
    sensor_storage,
    average_measurement_per_second_local
);
