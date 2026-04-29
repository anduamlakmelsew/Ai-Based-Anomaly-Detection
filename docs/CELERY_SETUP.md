# Celery + Redis Async Processing Setup Guide

This guide explains how to set up and run the AI Security Scanner with Celery for asynchronous background task processing.

## Overview

The scanner now supports **asynchronous scan execution** using Celery with Redis as the message broker. This provides:

- **Non-blocking API**: `/api/scan/start` returns immediately with a task ID
- **Background processing**: Scans run in separate worker processes
- **Scalability**: Multiple workers can process scans concurrently
- **Progress tracking**: Real-time updates via WebSocket and polling endpoint
- **Fault tolerance**: Automatic retries for failed tasks

## Architecture

```
┌─────────────┐     HTTP POST     ┌─────────────┐
│   Client    │ ─────────────────> │  Flask API  │
│  (React)    │                    │  (/start)   │
└─────────────┘                    └──────┬──────┘
                                          │
                                          │ Enqueue
                                          ▼
                                   ┌─────────────┐
                                   │Redis Broker │
                                   │  (Queue)    │
                                   └──────┬──────┘
                                          │
                                          │ Consume
                                          ▼
                                   ┌─────────────┐
                                   │Celery Worker│
                                   │ (run_scan)  │
                                   └──────┬──────┘
                                          │
                    ┌─────────────────────┼─────────────────────┐
                    │                     │                     │
                    ▼                     ▼                     ▼
            ┌─────────────┐      ┌─────────────┐      ┌─────────────┐
            │   Network   │      │    Web      │      │   System    │
            │   Scanner   │      │   Scanner   │      │   Scanner   │
            └─────────────┘      └─────────────┘      └─────────────┘
```

## Installation

### 1. Install Redis

**Ubuntu/Debian:**
```bash
sudo apt update
sudo apt install redis-server
sudo systemctl enable redis-server
sudo systemctl start redis-server
```

**macOS:**
```bash
brew install redis
brew services start redis
```

**Docker:**
```bash
docker run -d --name redis -p 6379:6379 redis:latest
```

**Verify Redis is running:**
```bash
redis-cli ping
# Should return: PONG
```

### 2. Install Python Dependencies

```bash
cd /home/andu/AI_Baseline_Assessment_Scanner/backend
source venv/bin/activate
pip install celery==5.4.0 redis==5.0.8
```

Or install all dependencies:
```bash
pip install -r requirements.txt
```

### 3. Configure Environment Variables

Add to your `backend/.env` file:

```env
# Redis Configuration
REDIS_URL=redis://localhost:6379/0

# Optional: Celery configuration
CELERY_WORKER_CONCURRENCY=4
CELERY_TASK_TIME_LIMIT=3600
```

## Running the System

### Option 1: Development Mode (Synchronous)

For development without Redis/Celery, set `sync: true` in the request:

```bash
curl -X POST http://localhost:5000/api/scan/start \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{"target": "example.com", "scan_type": "web", "sync": true}'
```

### Option 2: Production Mode (Asynchronous)

**Terminal 1: Start Flask API**
```bash
cd /home/andu/AI_Baseline_Assessment_Scanner/backend
source venv/bin/activate
python run.py
```

**Terminal 2: Start Celery Worker**
```bash
cd /home/andu/AI_Baseline_Assessment_Scanner/backend
source venv/bin/activate
celery -A app.celery_config.celery_app worker --loglevel=info
```

**Advanced: Multiple Workers**
```bash
# Run 4 concurrent workers
celery -A app.celery_config.celery_app worker --loglevel=info --concurrency=4

# Run with specific queue
celery -A app.celery_config.celery_app worker --loglevel=info -Q scans
```

**Terminal 3: Start Flower (Optional Monitoring UI)**
```bash
pip install flower
celery -A app.celery_config.celery_app flower --port=5555
# Access at http://localhost:5555
```

## API Usage

### Start a Scan (Async)

```bash
curl -X POST http://localhost:5000/api/scan/start \
  -H "Authorization: Bearer <jwt_token>" \
  -H "Content-Type: application/json" \
  -d '{"target": "example.com", "scan_type": "web"}'
```

**Response:**
```json
{
  "success": true,
  "message": "Scan queued for background processing",
  "scan_id": 123,
  "celery_task_id": "abc-123-def-456",
  "status": "queued",
  "check_status_url": "/api/scan/status/abc-123-def-456"
}
```

### Check Scan Status

```bash
curl http://localhost:5000/api/scan/status/abc-123-def-456 \
  -H "Authorization: Bearer <jwt_token>"
```

**Response (Queued):**
```json
{
  "success": true,
  "scan_id": 123,
  "celery_task_id": "abc-123-def-456",
  "task_state": "PENDING",
  "ready": false,
  "scan_status": "queued",
  "target": "example.com",
  "scan_type": "web"
}
```

**Response (In Progress):**
```json
{
  "success": true,
  "scan_id": 123,
  "celery_task_id": "abc-123-def-456",
  "task_state": "PROGRESS",
  "ready": false,
  "progress": 60,
  "stage": "Running security checks",
  "scan_status": "running"
}
```

**Response (Completed):**
```json
{
  "success": true,
  "scan_id": 123,
  "celery_task_id": "abc-123-def-456",
  "task_state": "SUCCESS",
  "ready": true,
  "successful": true,
  "scan_status": "completed",
  "result": { ... }
}
```

### WebSocket Progress Updates

The frontend can listen to WebSocket events for real-time progress:

```javascript
socket.on('scan_progress', (data) => {
  console.log(`Scan ${data.scan_id}: ${data.progress}% - ${data.stage}`);
});
```

## Database Migration

The Scan model has been updated with a new `celery_task_id` field. Run migrations:

```bash
cd /home/andu/AI_Baseline_Assessment_Scanner/backend
flask db migrate -m "Add celery_task_id to scans"
flask db upgrade
```

## Celery Configuration Details

### Task Retry Policy

Scans automatically retry on certain failures:
- **Max retries**: 3
- **Retry delay**: 60 seconds (with exponential backoff)
- **Retry on**: Database errors, connection errors
- **Max backoff**: 10 minutes

### Time Limits

- **Soft time limit**: 55 minutes (warning issued)
- **Hard time limit**: 60 minutes (task killed)
- **Result expiry**: 24 hours

### Rate Limiting

Maximum 10 scans per minute per worker to prevent overwhelming targets.

## Monitoring & Debugging

### View Celery Worker Logs

```bash
# In the terminal running the worker
# Look for:
# - [Celery Task <id>] Starting network scan...
# - [Celery Task <id>] Scan completed successfully
# - Task <name>[<id>] finished with state: SUCCESS
```

### Check Redis Queue

```bash
redis-cli
> LLEN celery
# Returns number of pending tasks

> LRANGE celery 0 -1
# View all tasks in queue
```

### Flower Dashboard

Access at `http://localhost:5555` to view:
- Active tasks
- Task success/failure rates
- Worker status
- Real-time task progress

## Troubleshooting

### "Celery initialization failed" Warning

This is normal if Redis isn't running. The API will fall back to synchronous mode automatically. To fix:

```bash
# Check Redis status
redis-cli ping

# If not running, start it
sudo systemctl start redis-server  # Linux
brew services start redis          # macOS
```

### Tasks Not Being Processed

1. **Check worker is running:**
   ```bash
   ps aux | grep celery
   ```

2. **Check Redis connection:**
   ```bash
   redis-cli ping
   ```

3. **Verify task is queued:**
   ```bash
   redis-cli LLEN celery
   ```

4. **Check worker logs for errors**

### Database Connection Errors in Workers

Workers need access to the same database as the Flask app. Ensure:
- `DATABASE_URL` is set correctly in `.env`
- Database is accessible from worker processes

### WebSocket Not Receiving Updates

Celery workers emit WebSocket updates via SocketIO. Ensure:
- Flask-SocketIO is using Redis message queue for multi-process support:
  ```python
  socketio = SocketIO(message_queue='redis://localhost:6379/0')
  ```

## Production Deployment

### Docker Compose Example

```yaml
version: '3.8'

services:
  api:
    build: ./backend
    ports:
      - "5000:5000"
    environment:
      - REDIS_URL=redis://redis:6379/0
    depends_on:
      - redis
      - db

  worker:
    build: ./backend
    command: celery -A app.celery_config.celery_app worker --loglevel=info --concurrency=4
    environment:
      - REDIS_URL=redis://redis:6379/0
    depends_on:
      - redis
      - db
    deploy:
      replicas: 2

  redis:
    image: redis:7-alpine
    volumes:
      - redis_data:/data

  db:
    image: postgres:15
    environment:
      - POSTGRES_DB=ai_scanner
      - POSTGRES_USER=scanner_user
      - POSTGRES_PASSWORD=secure_password
    volumes:
      - postgres_data:/var/lib/postgresql/data

volumes:
  redis_data:
  postgres_data:
```

## Scaling Considerations

### Horizontal Scaling

Run multiple worker instances across different machines:
```bash
# Machine 1
celery -A app.celery_config.celery_app worker --loglevel=info -n worker1@%h

# Machine 2
celery -A app.celery_config.celery_app worker --loglevel=info -n worker2@%h
```

### Queue Separation

For different scan types or priorities:
```python
# High priority scans
run_security_scan.apply_async(args=[...], queue='high_priority')

# Regular scans
run_security_scan.apply_async(args=[...], queue='default')
```

Run separate workers per queue:
```bash
celery -A app.celery_config.celery_app worker -Q high_priority --loglevel=info
celery -A app.celery_config.celery_app worker -Q default --loglevel=info
```

## What Changed & Why

### Changes Made

1. **New Files:**
   - `app/celery_config.py` - Celery app configuration
   - `app/tasks/__init__.py` - Tasks package
   - `app/tasks/scan_tasks.py` - Celery task definitions
   - `docs/CELERY_SETUP.md` - This guide

2. **Modified Files:**
   - `app/models/scan_model.py` - Added `celery_task_id` field
   - `app/services/scan_service.py` - Added async helper functions
   - `app/routes/scan_routes.py` - Async scan endpoint, status endpoint
   - `app/__init__.py` - Celery initialization
   - `requirements.txt` - Added celery, redis

3. **New API Endpoints:**
   - `POST /api/scan/start` - Now returns immediately (async)
   - `GET /api/scan/status/<task_id>` - Check task progress

### Why This Improves Scalability

| Aspect | Before (Sync) | After (Async) |
|--------|---------------|---------------|
| **API Response Time** | Seconds to minutes (blocking) | <100ms (immediate) |
| **Concurrent Scans** | 1 per API process | Unlimited (queued) |
| **Resource Usage** | Blocks during scan | Free immediately |
| **Failure Recovery** | Manual restart | Auto-retry with backoff |
| **Horizontal Scaling** | Not possible | Multiple workers |
| **Monitoring** | Limited | Full task tracking |

### Backward Compatibility

- **Synchronous mode** still available via `"sync": true` flag
- **Existing endpoints** work unchanged
- **Database schema** backward compatible (nullable field added)
- **WebSocket events** remain identical

## Summary

The Celery integration transforms the security scanner from a synchronous, blocking API into an asynchronous, scalable system capable of handling multiple concurrent scans across distributed workers.

**Key Benefits:**
- ✅ Non-blocking API responses
- ✅ Background task processing
- ✅ Automatic retries and error handling
- ✅ Real-time progress tracking
- ✅ Horizontal scalability
- ✅ Production-ready monitoring
