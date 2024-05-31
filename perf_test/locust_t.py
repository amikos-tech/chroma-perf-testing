import json
import os
import random
import time
import uuid
from base64 import b64encode
import pandas as pd
import requests

from chromadb import Settings
from locust import task, User, events, between, tag

import chromadb


@events.init_command_line_parser.add_listener
def _(parser):
    parser.add_argument("--chroma-host", type=str, default="localhost",
                        help="Chroma host")
    parser.add_argument("--port", type=int, default=8000,
                        help="Chroma port")
    parser.add_argument("--auth-type", type=str, default=os.getenv("CHROMA_AUTH_TYPE"), )
    parser.add_argument("--auth-credentials", type=str, default=os.getenv("CHROMA_AUTH_CREDENTIALS"), )
    parser.add_argument("--dataset", type=str, default=os.getenv("PERF_TEST_DATASET","unknown"), )
    parser.add_argument("--test-run-id", type=str, default=os.getenv("PERF_TEST_RUN_ID","local"), )
    parser.add_argument("--config-id", type=str, default=os.getenv("CHROMA_CONFIG_ID","local"), )
    parser.add_argument("--chroma-version", type=str, default=os.getenv("CHROMA_VERSION","main"), )


class UserBehavior(User):
    wait_time = between(0.001, 0.002)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        try:

            self.client = chromadb.HttpClient(host=self.environment.parsed_options.chroma_host,
                                              port=self.environment.parsed_options.port,
                                              settings=Settings(anonymized_telemetry=False))
            data_str = os.getenv('LOCUST_JSON')
            data = json.loads(data_str)
            self.query = data['query']
            self.id = data['id']
            self.tags = data['tags']
            self.collection = self.client.get_collection("test")
            self.user_id = str(uuid.uuid4())


        except Exception as e:
            print(e)
            raise e

    def on_start(self):
        print("Starting up")

    @task
    def collection_get(self):
        start_time = time.perf_counter()
        req_metadata = {
            "request_type": "chroma",
            "name": f"{self.id}",
            "start_time": start_time,
            "response_length": 0,
            "response": None,
            "context": {
                "query": json.dumps(self.query),
                "tags": json.dumps(self.tags),
                "user_id": self.user_id,
                "dataset": self.environment.parsed_options.dataset,
                "test_run_id": self.environment.parsed_options.test_run_id,
                "config_id": self.environment.parsed_options.config_id,
                "chroma_version": self.environment.parsed_options.chroma_version,
            },
            "exception": None,
        }
        try:
            self.collection.get(where=self.query)
            total_time = int((time.perf_counter() - start_time) * 1000)
            req_metadata["response_time"] = total_time
            events.request.fire(**req_metadata)
        except Exception as e:
            total_time = int((time.perf_counter() - start_time) * 1000)
            req_metadata["response_time"] = total_time
            req_metadata["exception"] = str(e)
            events.request.fire(**req_metadata)


stats_data = []


@events.request.add_listener
def on_request(request_type, name, response_time, response_length, response, context, exception, **kwargs):
    stats_data.append({
        "user_id": context.get("user_id"),
        "request_type": request_type,
        "name": name,
        "query": context.get("query"),
        "tags": json.loads(context.get("tags")),
        "response_time": response_time,
        "response_length": response_length,
        "exception": exception,
        "dataset": context.get("dataset"),
        "test_run_id": context.get("test_run_id"),
        "config_id": context.get("config_id"),
    })


@events.quitting.add_listener
def save_stats_to_dataframe(environment):
    df_merged = pd.DataFrame()
    if os.path.exists('merged_locust_data.parquet'):
        df_merged = pd.read_parquet('merged_locust_data.parquet')
    df = pd.DataFrame(stats_data)
    # Save DataFrame to a CSV file
    df_merged = pd.concat([df_merged, df], ignore_index=True)
    df_merged.to_parquet('merged_locust_data.parquet', index=False)
