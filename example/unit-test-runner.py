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
api_server = "127.0.0.1:8080"
api_url = f"http://{api_server}/api/v1/eval"

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler(log_file, "w", "utf-8"),
        logging.StreamHandler(),  # Log to stdout
    ]
)

# Initialize failure count
failed_tests = 0

# util function to check if csv is as expected
required_columns = {"id", "description", "file", "dest_host", "src_ip", "expected_output", "required_flags"}
def validate_csv_columns(df):
    """
    Validate that all required columns are present in the CSV file.

    :param df: The pandas DataFrame loaded from the CSV file.
    :return: A bool "is_valid" indicating success.
    """
    missing_columns = required_columns - set(df.columns)
    if missing_columns:
        logging.error(f"The file 'is missing required column(s): {', '.join(missing_columns)}")
        return False
    return True


# Load all test cases
csv_files = glob.glob(os.path.join(tests_dir, "**", "*.test.csv"), recursive=True)


# Recursively list all files in pacs/ using glob.glob
available_files = [
    os.path.relpath(os.path.abspath(f), os.path.abspath(pacs_dir))
    for f
    in glob.glob(os.path.join(pacs_dir, "**", "*"), recursive=True)
    if os.path.isfile(f)
]

# log header
logging.info("Test Execution Log")
logging.info(f"Found the following Assets: (test-csv-files= {len(csv_files)}, pac-files={len(available_files)})")
logging.info("==================")

# Helper function to match files with wildcard
def find_matching_files(pattern):
    return [f for f in available_files if fnmatch(f, pattern)]

for csv_file in csv_files:
    df = pd.read_csv(csv_file)
    if not validate_csv_columns(df):
        continue
    df["source_file"] = os.path.relpath(os.path.abspath(csv_file), os.path.abspath(tests_dir))
    df["required_flags"] = df["required_flags"].fillna("")
    test_cases = df.to_dict("records")
    logging.info(f"= csv file '{csv_file}'")

    # Execute tests
    for test in test_cases:
        logging.info(f"== test-case {int(test['id']):03d}/{len(test_cases):03d}: '{test['description']}'")
        try:
            file_pattern = test["file"]
            matching_files = find_matching_files(file_pattern)

            for file_path in matching_files:
                logging.info(f"=== pac file {file_path}")
                with open(os.path.join(pacs_dir, file_path), "r") as file:
                    file_content = file.read()

                # Prepare JSON payload
                payload = {
                    "dest_host": test["dest_host"],
                    "src_ip": test["src_ip"],
                    "content": file_content,
                }

                # API call
                response = requests.post(api_url, json=payload)
                response_json = response.json()

                if response.status_code != 200 or response_json.get("status") != "success":
                    logging.error(f"    ❌FAIL: Request for file '{file_path}' failed. Response: {json.dumps(response_json)}")
                    failed_tests += 1
                else:
                    results = response_json.get("results", [])
                    for result in results:
                        if test['required_flags'] != "" and test['required_flags'] not in result.get('flags', []):
                            logging.info(f"    ❔SKIPPED (engine '{result['engine']}'): Missing flags")
                            # skip engine if it does not support the feature we need
                            continue

                        if result.get("status") != "success":
                            logging.error(f"    ❌FAIL (engine '{result['engine']}'): Engine reported problems. error {result['error_code']}: {result['error']}.\n{result['message']}\nFull Response: {json.dumps(result)}")
                            failed_tests += 1
                            continue

                        if 'evaluation' in result.get('flags', []):
                            # if evaluation is supported we check roxy resulting from the evaluation
                            if test['expected_output'] != result['proxy']:
                                logging.error(f"    ❌FAIL (engine '{result['engine']}'): Invalid Proxy. Expected: {test['expected_output']}, Actual: {result['proxy']}")
                                failed_tests += 1
                                continue

                        # no check failed, so we pass
                        logging.info(f"    ✅PASS (engine '{result['engine']}'): Test succeeded.")

        except Exception as e:
            logging.error(f"   ERROR: Exception during tests. Error: {str(e)}")
            failed_tests += 1

# Exit with failure count as the status code
exit(failed_tests)
