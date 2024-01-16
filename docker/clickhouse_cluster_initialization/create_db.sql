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
