#!/bin/bash

echo "Starting WinHTTP engine..."

xvfb-run --auto-servernum --server-args="-screen 0 1024x768x16" wine python.exe winhttp.py &
PID=$!
echo "WinHTTP Engine started with PID: $PID"
wait $PID
