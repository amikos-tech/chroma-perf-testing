import os
import random
import time
import uuid
from base64 import b64encode

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
    parser.add_argument("--dataset", type=str, default=os.getenv("CHROMA_DATASET"), )


class UserBehavior(User):
    wait_time = between(0.001, 0.002)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        try:
            self._session = requests.Session()

            # self.client = chromadb.HttpClient(host=self.environment.parsed_options.chroma_host,
            #                                   port=self.environment.parsed_options.port,
            #                                   settings=Settings(anonymized_telemetry=False,
            #                                                     chroma_client_auth_provider=provider,
            #                                                     chroma_client_auth_credentials=credentials))


        except Exception as e:
            print(e)
            raise e

    def on_start(self):
        print(self.environment.parsed_options.auth_type)
        if self.environment.parsed_options.auth_type == "basic":
            credentials = self.environment.parsed_options.auth_credentials
            encoded_creds = b64encode(bytes(f'{credentials}', 'utf-8')).decode('utf-8')
            self._session.headers.update({"Authorization": f"Basic {encoded_creds}"})
            print(f"Basic {encoded_creds}")
        if self.environment.parsed_options.auth_type == "token":
            credentials = self.environment.parsed_options.auth_credentials
            self._session.headers.update({"Authorization": f"Bearer {credentials}"})

    @task
    def list_collections(self):
        start_time = time.perf_counter()
        req_metadata = {
            "request_type": "chroma",
            "name": "list_collections",
            "start_time": start_time,
            "response_length": 0,
            "response": None,
            "context": {},  # see HttpUser if you actually want to implement contexts
            "exception": None,
        }
        try:
            self._session.get(
                f"http://{self.environment.parsed_options.chroma_host}:{self.environment.parsed_options.port}/api/v1/collections")
            total_time = int((time.perf_counter() - start_time) * 1000)
            req_metadata["response_time"] = total_time
            events.request.fire(**req_metadata)
        except Exception as e:
            total_time = int((time.perf_counter() - start_time) * 1000)
            req_metadata["response_time"] = total_time
            req_metadata["exception"] = e
            events.request.fire(**req_metadata)
