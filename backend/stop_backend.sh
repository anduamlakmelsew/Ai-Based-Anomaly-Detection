#!/bin/bash

# Backend Stop Script
# Cleanly stops all backend processes

PORT=5002

echo "🛑 Stopping backend..."

# Kill process on port
PID=$(lsof -ti:$PORT 2>/dev/null)
if [ ! -z "$PID" ]; then
    echo "⚠️  Killing process $PID on port $PORT..."
    kill -9 $PID 2>/dev/null
fi

# Kill any Python processes running run.py
echo "🔍 Killing Python processes..."
pkill -9 -f "python.*run.py" 2>/dev/null

# Kill any Celery workers
echo "🔍 Killing Celery workers..."
pkill -9 -f "celery.*worker" 2>/dev/null

echo "✅ Backend stopped"

