CREATE DATABASE IF NOT EXISTS sensor_storage
ON CLUSTER sensor_data_cluster_2S_2R;

-- Create local table
CREATE TABLE IF NOT EXISTS sensor_storage.sensors_data
ON CLUSTER sensor_data_cluster_2S_2R
(
    sensor_id UInt32,
    timestamp Float32,
    measurement Float32
)
ENGINE = ReplicatedMergeTree('/clickhouse/tables/{shard}/sensors_data', '{replica}')
ORDER BY (sensor_id, timestamp, measurement);

-- Create distributed table
CREATE TABLE IF NOT EXISTS sensor_storage.sensors_data_distributed
ON CLUSTER sensor_data_cluster_2S_2R
AS sensor_storage.sensors_data
ENGINE = Distributed(sensor_data_cluster_2S_2R, sensor_storage, sensors_data, xxHash64(sensor_id));