#!/bin/bash

echo "Starting eslint engine..."

npm start &
PID=$!
echo "eslint Engine started with PID: $PID"
wait $PID
