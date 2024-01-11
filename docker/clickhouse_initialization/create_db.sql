-- Create a new database
CREATE DATABASE IF NOT EXISTS sensor_storage;

-- Use the newly created database
USE sensor_storage;

-- Create new tables
CREATE TABLE IF NOT EXISTS sensors_data
(
    sensor_id UInt32,
    timestamp Float,
    measurement Float32
)
ENGINE = MergeTree
PRIMARY KEY (sensor_id, timestamp);