#!/bin/bash

# Backend Startup Script
# Ensures only one instance runs on port 5002

PORT=5002
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "🔍 Checking for existing processes on port $PORT..."

# Kill any existing process on the port
PID=$(lsof -ti:$PORT 2>/dev/null)
if [ ! -z "$PID" ]; then
    echo "⚠️  Found process $PID on port $PORT, killing it..."
    kill -9 $PID 2>/dev/null
    sleep 1
fi

# Kill any zombie Python processes running run.py
echo "🔍 Checking for zombie Python processes..."
pkill -9 -f "python.*run.py" 2>/dev/null
sleep 1

# Activate virtual environment
echo "🔧 Activating virtual environment..."
cd "$SCRIPT_DIR"
source venv/bin/activate

# Start the backend
echo "🚀 Starting backend on port $PORT..."
python run.py

