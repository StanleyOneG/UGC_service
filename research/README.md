# Research data storage

## Computer configuration

| RAM    | CPU |     OS     | Storage |
|:------:|:---:|------------|---------|
|  30GB  |  10 | Debian 11  |   SSD   |

## Results

**Read data**

|     Name           | № Requests  | Avg response time (ms) |   Avg RPS       |
|:-------------------|:-----------:|:----------------------:|:---------------:|
|   **ClickHouse**   |    39320    |          290           |        391      |
|   Vertica          |    3933     |          6000          |        64.5     |

**Inserting data**

|     Name           | № Requests  | Avg response time (ms) |   Avg RPS       |
|:-------------------|:-----------:|:----------------------:|:---------------:|
|   **Kafka**        |    398554   |          350           |      1647.9     |
|   EventStore       |    272632   |          54000         |      1115.8     |
