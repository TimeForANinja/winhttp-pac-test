#!/bin/bash

echo "Waiting for Docker to initialize..."
sleep 10

# Function to gracefully clean up all process IDs
cleanup() {
  echo "Cleaning up processes..."
  for PID in "${PIDS[@]}"; do
    kill "$PID" 2>/dev/null || true
  done
}

# Track all running process IDs
PIDS=()

# Start each engine's start.sh script
for engine in engines/*; do
  if [ -d "$engine" ] && [ -f "$engine/start.sh" ]; then
    echo "Starting $engine/start.sh..."

    # Run the start.sh script in the engine folder inside a subshell
    env -C "$engine" bash "./start.sh" &
    PIDS+=($!) # Add process ID to the list

  else
    echo "Warning: $engine is not a valid engine folder or missing start.sh"
  fi
done

# Start the core python server.py script
# And add the process ID to the list
echo "Starting core python server.py..."
. venv/bin/activate && cd app && python3 server.py &
PIDS+=($!)

# Trap script termination to clean up all running processes
trap cleanup EXIT

# Wait for any of the processes to terminate
echo "Waiting for processes to terminate..."
wait -n

# If any process stops, clean up remaining processes
echo "One of the processes has stopped. Cleaning up others..."
cleanup

# Exit script with the exit code of the first process that stopped
exit $?
