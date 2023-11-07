-- Create a new database
CREATE DATABASE IF NOT EXISTS sensor_storage;

-- Use the newly created database
USE sensor_storage;

-- Create new tables
CREATE TABLE IF NOT EXISTS sensor_0
(
    record_id UInt32,
    timestamp DateTime,
    measurment Float32
)
ENGINE = MergeTree
PRIMARY KEY (record_id, timestamp);

CREATE TABLE IF NOT EXISTS sensor_1
(
    record_id UInt32,
    timestamp DateTime,
    measurment Float32
)
ENGINE = MergeTree
PRIMARY KEY (record_id, timestamp);
