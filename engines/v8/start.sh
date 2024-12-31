#!/bin/bash

echo "Starting v8 engine..."

npm start &
PID=$!
echo "V8 Engine started with PID: $PID"
wait $PID
