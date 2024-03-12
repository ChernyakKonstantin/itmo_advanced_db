# Designing the timeseries storage system.

There is a set of high-frequency sensors (up to 1000 sensors, each 1 kHz) that generate data every second. We can assume that the data is sent to storage by already formed batches coming from some intermediate system that has the ability for very short-term storage (up to 3-4 seconds), and is also unreliable. It should be noted that due to the imperfection of the device of the sensors themselves and the specified intermediate system, some data may be significantly delayed.

The generated data must be written to some storage/database for permanent storage. Requests will be made to this storage to ensure the operation of the “lenses” system (data lenses) associated with the visualization of aggregated time series for the user interface. Each of the lenses involves viewing a certain time interval selected by the user (for example, 10 seconds, 1 minute, or 1 hour), specially aggregated into such a number of points that can be displayed on the screen (for example, the interval of 1 minute for a 1 kHz sensor is 60,000 points, which are aggregated (roll up) into 2500 points by finding the average for each 60000 / 2500 = 24 consecutive points). A user can request from 1 to 10 sensors with the same time interval within a single request, and several users (up to a hundred) can work with the storage at once. Storage conditions mean that there may be short-term failures of nodes where the storage is deployed or networks before them (up to 1 min.).

You need to design a storage together with the data loading system (ingestion), if necessary, that would meet the following functional conditions:

- Queries must be correct, i.e. they must always return the value that would have been obtained if the “raw” data was accessed directly.
- Fast data acquisition, i.e. there should not be a scan of “raw” data with their full aggregation.
- It is advisable to avoid writing to the storage too often.
- Small data loss during recording is allowed.*

*If you are able to explain the compromise.

There are several variants related to data losing:

1. 	No data losing in raw data + No data losing in lenses (in this case you will get extra points).

2. 	No data losing in raw data + Some data is lost in lenses.

3. 	Some data is lost in raw data + Some data is lost in lenses.

Perfect case (additional condition):

1. 	There are no duplicate records in raw data and lenses (in this case you will also get extra points).

Requirements:

1. 	Use ClickHouse as a main storage.

2. 	Sharding and replication (at least 4 servers).

3. 	Data volume being stored should contain at least one month of data  (quantity of sensors and their frequency see earlier in the text).

4. 	Data generator(-s) and ingestion procedure is a must (note: one may use Kafka to reliably insert data).

5. 	Generators of request workload should be implemented. The storage should be able to insert and process select queries simultaneously.

6. 	Test scenarios should be implemented as a demo of the solution.

7. Bare-metal deployment is forbidden. Deploy the storage with replicas, queues, generators, requesters and other modules using Kubernetes, docker (see: Kubernetes’ StatefulSet / Deployment / Job, etc.)

# Launch in k8s

1. Launch `run.sh` in `k8s/zookeeper`. It starts Zookeeper.
2. Launch `run.sh` in `k8s/clickhouse`. It starts ClickHouse.
3. Launch `run.sh` in `k8s/kafka`. It start Kafka broker.
4. Launch `run.sh` in `k8s/kafka-clickhouse-connector`. It starts Kafka Connect. Wait for it to get ready.
5. Launch `run.sh` in `k8s/sensors`. It launches Clickhouse Sink Connector and then starts sending Sensors data.
6. Launch `run.sh` in `k8s/clickhouse_aggregator`. It launches Clickhouse aggregation jobs. Currently it emulates CronJob.
7. Launch `run.sh` in `k8s/lenses`. It launches Lenses application (data viewer).

# Stopping in k8s
Run `del_all.sh` in `k8s`.