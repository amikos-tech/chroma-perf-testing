import argparse
import os
import subprocess
import json


def run_locust_with_env(jsonl_file):
    with open(jsonl_file, 'r') as file:
        for line in file:
            # Convert JSON line to a dictionary
            data = json.loads(line)
            # Convert dictionary back to JSON string for the environment variable
            env_var = json.dumps(data)
            # Set the environment variable
            env = {"LOCUST_JSON": env_var}
            # Run locust using subprocess
            print(f"Starting single user test for : {data['id']}")
            command = ['poetry', 'run', 'locust', '-f', 'perf_test/locust_t.py', '--headless', '-u', '1', '-r', '1',
                       '--run-time', os.getenv("PERF_TEST_DURATION", "1m"), '--csv=results_${size}']
            subprocess.run(command, env=env)
            print(f"Starting multi user (5) test for : {data['id']}")
            command = ['poetry', 'run', 'locust', '-f', 'perf_test/locust_t.py', '--headless', '-u',
                       os.getenv("PERF_TEST_CONCURRENT_USERS", "5"), '-r', '1',
                       '--run-time', os.getenv("PERF_TEST_DURATION", "1m"), f"--csv=results_${data['id']}"]
            subprocess.run(command, env=env)


if __name__ == "__main__":
    ar = argparse.ArgumentParser()
    ar.add_argument("--queries-file", type=str, required=True, help="Path to the queries JSONL file")
    run_locust_with_env(ar.parse_args().jsonl_file)