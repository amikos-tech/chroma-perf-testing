# Chroma Performance Test Benchmarking Framework

## Components

- Chroma server
- Chroma client
- Dataset
- Chroma Performance Test Executor (based on locust)


## Datasets

There are two ways to deal with datasets:

- ready-made archives that can be unarchived under persist dir
- imported from huggingface datasets

We'd go for option 1 for now as it is the most straightforward. We'll curate a few datasets with the following characteristics:

- 100k records
- 250k records
- 500k records
- 1M records

All sets will have metadata as follows:

- 2 int fields - random int between 1 and 100, and current date in epoch | needed for testing range queries
- 2 string fields - needed for testing eq and neq queries
- 1 bool field - needed for testing
- 2 float fields - needed for testing range queries

## Queries

List of queries to be tested:

- simple query without any filters - `collection.query(query_texts=["my query"])`
- Query with eq filter
- Query with multiple eq filters (two for now)
- Query with range filter on int field
- Query with range and eq filter
- Query with in/nin filter
- Query with all filters

To query we have two approaches:

- get a random entry from the original dataset (works when using HF datasets)
- get a random record from the collection and use that to construct the query - impact on performance

Things to consider:

- concurrent queries - we can have the same query executed with single and multiple users.
- warm-up query - all tests should have a warm-up query to ensure the server is ready to handle the load.
- All tests should send at least a few queries if not more to ensure any variations.


## Collecting Metrics

We'll collect metrics from client perspective: however it would be useful to also get metrics from the server perspective.

Client metrics will be collected with locust exports to CSV. We'll collect the following metrics:

- response time
- query type


## Test setup

This can run in a matrix test where each run will test a different dataset size which will also run a series of query tests. 

Create individual EC2 for each dataset size. Create a single EC2 for the test executor. Create an EC2 to collect metrics.
Reports are stored in S3.



(chromadb-hfds-py3.9) [chroma-hfds] cat big_collection.jsonl | head -1 | cdp id --uuid | cdp meta -m product=L9400 -m test=1 -m b=ok -m a=1.2 -m c=another -m d=x11 -m e=1000 -m f=3d32 -m g=3.21 | pv -L 30000k | cdp import "file:///Users/tazarov/experiments/chroma/oss/fujitsu/chroma2/test1" --create  --batch-size 10000 --all-meta

## Dataset layout

- `chroma/` - the persist dir
- `query_plan.jsonl` - the query plan to execute for this performance test


### Query Plan

The query plan contains the specific query to execute along with information about how many concurrent requests and for how long.

    ```json
    {
        "query": {"$eq": {"product": "L9400"}},
        "concurrent_users": 1,
        "duration": "1m"
    }
    ```

