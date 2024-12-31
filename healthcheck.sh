#!/bin/bash

# core server - Check the /up endpoint on port 8080
if ! curl --silent --fail http://localhost:8080/up; then
  echo "Health check failed for http://localhost:8080/up"
  exit 1
fi

# v8 engine - Check the /up endpoint on port 8081
if ! curl --silent --fail http://localhost:8081/up; then
  echo "Health check failed for http://localhost:8081/up"
  exit 1
fi

# winhttp engine - Check the /up endpoint on port 8082
if ! curl --silent --fail http://localhost:8082/up; then
  echo "Health check failed for http://localhost:8082/up"
  exit 1
fi

# eslint engine - Check the /up endpoint on port 8083
if ! curl --silent --fail http://localhost:8083/up; then
  echo "Health check failed for http://localhost:8083/up"
  exit 1
fi

# If all endpoints are healthy
echo "Health check passed"
exit 0
