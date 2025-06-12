#!/bin/bash
set -euo pipefail

# Function to handle Ctrl+C
cleanup() {
    echo "Stopping servers..."
    kill "$PID1" "$PID2"
    wait "$PID1" "$PID2" 2>/dev/null
    exit
}

# Trap SIGINT (Ctrl+C)
trap cleanup SIGINT


# Start the API server
(cd api_endpoints/v1_postcode_lookup/ && uv run uvicorn app:app --reload) &
PID1=$!
echo "---"
echo "API started (PID $PID1)"
echo "API server listening on port 8000"
echo "---"

# Start website
uv run manage.py runserver 8001 &    # Replace with your server command
PID2=$!
echo "Web server started (PID $PID2)"
echo "Web server listening on port 8001"
echo "---"

# Wait for both servers
wait "$PID1" "$PID2"
