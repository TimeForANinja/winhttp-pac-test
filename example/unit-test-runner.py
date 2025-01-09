import os
import glob
import pandas as pd
import requests
import json
import logging
from fnmatch import fnmatch


# Define directories
tests_dir = "tests/"
pacs_dir = "pacs/"
log_file = "test_log.txt"
api_server = "localhost:8080"
api_url = f"http://{api_server}/api/v1/eval"

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler(log_file),
        logging.StreamHandler(),  # Log to stdout
    ]
)
logging.info("Test Execution Log")
logging.info("==================")

# Initialize failure count
failed_tests = 0

# Load all test cases
csv_files = glob.glob(os.path.join(tests_dir, "**", "*.test.csv"), recursive=True)
test_cases = []

for csv_file in csv_files:
    df = pd.read_csv(csv_file)
    df["source_file"] = os.path.relpath(os.path.abspath(csv_file), os.path.abspath(tests_dir))
    test_cases.extend(df.to_dict("records"))

# Recursively list all files in pacs/ using glob.glob
available_files = [
    os.path.relpath(os.path.abspath(f), os.path.abspath(pacs_dir))
    for f
    in glob.glob(os.path.join(pacs_dir, "**", "*"), recursive=True)
    if os.path.isfile(f)
]
logging.info(f"Found the following Assets:\ntest csv files: {len(csv_files)}, test_cases: {len(test_cases)}, pac files: {len(available_files)}")

# Helper function to match files with wildcard
def find_matching_files(pattern):
    return [f for f in available_files if fnmatch(f, pattern)]

# Execute tests
for test in test_cases:
    try:
        file_pattern = test["file"]
        matching_files = find_matching_files(file_pattern)

        for file_path in matching_files:
            with open(os.path.join(pacs_dir, file_path), "r") as file:
                file_content = file.read()

            # Prepare JSON payload
            payload = {
                # todo: add the http:// on the backend
                # todo: make sure src_ip is an ip and no fqdn
                "dest_host": "http://" + test["dest_host"],
                "src_ip": "http://" + test["src_ip"],
                "content": file_content,
            }
            print("payload", payload)

            # API call
            response = requests.post(api_url, json=payload)
            response_json = response.json()

            if response.status_code == 200 and response_json.get("status") == "success":
                logging.info(f"PASS: Test for file '{file_path}' succeeded.")
            else:
                logging.error(f"FAIL: Test for file '{file_path}' failed. Response: {json.dumps(response_json)}")
                failed_tests += 1

    except Exception as e:
        logging.error(f"ERROR: Exception during test for file '{test.get('file', 'Unknown')}'. Error: {str(e)}")
        failed_tests += 1

# Exit with failure count as the status code
exit(failed_tests)
