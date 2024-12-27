#!/bin/bash

echo "Starting nodejs engine..."

npm start &
PID=$!
echo "V8 Engine started with PID: $PID"
wait $PID
