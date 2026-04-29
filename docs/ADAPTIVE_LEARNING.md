# Adaptive Learning Architecture

This document describes the adaptive learning system that enables the AI security scanner to improve over time based on analyst feedback.

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           ADAPTIVE LEARNING LOOP                             │
└─────────────────────────────────────────────────────────────────────────────┘

  ┌──────────────┐      ┌──────────────┐      ┌──────────────┐
  │   Inference  │─────▶│   Feedback   │─────▶│  Retraining  │
  │   Pipeline   │      │   Capture    │      │   Pipeline   │
  └──────────────┘      └──────────────┘      └──────────────┘
         ▲                                              │
         │                                              │
         │         ┌──────────────┐                   │
         └─────────│ Model Update │◀──────────────────┘
                   │   & Deploy   │
                   └──────────────┘
```

## Components

### 1. Inference Pipeline (Unchanged)

The existing AI inference pipeline continues to work as-is:

```python
# Existing flow - no changes needed
scan_result ──▶ AI Pipeline ──▶ Prediction ──▶ User Dashboard
                   │
                   ▼
            AIDetectionEvent (stored)
```

**Key Point:** Inference is completely separate from training. Models can be updated without disrupting active scans.

### 2. Feedback Capture System

**Database Table:** `ai_feedback`

| Column | Purpose |
|--------|---------|
| `id` | Primary key |
| `scan_id` | Link to scan |
| `prediction` | AI's original prediction |
| `corrected_label` | Analyst's corrected label |
| `source_type` | network/system/web |
| `used_for_training` | Whether incorporated into model |
| `high_confidence_wrong` | Flag for confident but incorrect predictions |

**API Endpoint:** `POST /api/ai/feedback`

```json
{
  "scan_id": 123,
  "prediction": "safe",
  "corrected_label": "vulnerable",
  "original_risk_level": "LOW",
  "corrected_risk_level": "HIGH",
  "feedback_notes": "AI missed SQL injection in login form",
  "source_type": "web"
}
```

**Why This Matters:**
- High-confidence wrong predictions (`confidence > 0.8`) are flagged for priority review
- Feedback is stored with metadata for analysis
- Unused feedback is tracked for incremental training

### 3. Retraining Pipeline

**Celery Task:** `retrain_models_with_feedback`

Runs periodically (default: daily at 2 AM) to:

1. **Check Feedback Threshold**
   - Minimum 50 new feedback records required
   - Skips if insufficient data (configurable)

2. **Backup Current Models**
   - Creates timestamped backup in `models/backups/`
   - Enables rollback if new models perform worse

3. **Prepare Training Data**
   ```python
   training_data = {
       'network': [feedback_records],
       'system': [feedback_records],
       'web': [feedback_records]
   }
   ```

4. **Incremental Training**
   - Retrains each model type independently
   - Uses feedback + original training data
   - Validates on held-out test set

5. **Atomic Model Swap**
   ```bash
   # Symlink approach enables zero-downtime updates
   network_model_v1.pkl  (old)
   network_model_v2.pkl  (new)
   network_model.pkl ──▶ network_model_v2.pkl  (symlink)
   ```

6. **Mark Feedback as Used**
   - Prevents duplicate training on same data
   - Tracks which model version incorporated feedback

### 4. Clean Separation

| Aspect | Implementation |
|--------|----------------|
| **Inference** | Reads from `*.pkl` files via symlinks |
| **Training** | Creates new `*_v{version}.pkl` files |
| **Deployment** | Updates symlinks atomically |
| **Rollback** | Restore from `models/backups/` |

**Critical:** Inference never writes to models; training never reads during inference.

## How It Makes the System Adaptive

### Before (Static AI)

```
Scan ──▶ AI Model (v1.0) ──▶ Prediction
              │
              │ (never changes)
              ▼
         Same accuracy forever
```

### After (Adaptive AI)

```
Scan ──▶ AI Model (v1.0) ──▶ Prediction ──▶ Analyst Review
                                           │
                                           ▼
                                    Feedback Captured
                                           │
                                           ▼
                              Retrain Model (v1.1)
                                           │
                                           ▼
Scan ──▶ AI Model (v1.1) ──▶ Prediction ──▶ (More accurate!)
              │
              │ (improved from feedback)
              ▼
         Better accuracy over time
```

## Key Improvements

1. **Accuracy Improvement**
   - Models learn from analyst corrections
   - High-confidence errors are prioritized
   - Domain-specific improvements (e.g., better SQL injection detection)

2. **Customization**
   - Each deployment learns organization-specific patterns
   - Adapts to unique infrastructure
   - Reduces false positives for environment

3. **Continuous Learning**
   - Daily retraining with new feedback
   - No manual model updates required
   - Automatic deployment of improvements

4. **Safety**
   - Model backups enable rollback
   - Validation before deployment
   - Inference never disrupted

## API Endpoints

### Submit Feedback
```bash
POST /api/ai/feedback
Authorization: Bearer <token>
Content-Type: application/json

{
  "scan_id": 123,
  "prediction": "safe",
  "corrected_label": "vulnerable",
  "source_type": "web",
  "feedback_notes": "Missed SQL injection"
}
```

**Response:**
```json
{
  "success": true,
  "feedback_id": 456,
  "high_confidence_correction": true
}
```

### View Feedback Stats
```bash
GET /api/ai/feedback/stats?days=30
```

**Response:**
```json
{
  "success": true,
  "data": {
    "overall": {
      "total_feedback": 150,
      "untrained_feedback": 45,
      "high_confidence_wrong": 12,
      "by_source_type": {
        "network": 50,
        "system": 30,
        "web": 70
      }
    },
    "user_contributions": 25
  }
}
```

### View Feedback History
```bash
GET /api/ai/feedback/history?limit=50&source_type=web
```

## Running the System

### Development Mode

Run retraining manually:

```python
from app.tasks.model_retraining_tasks import retrain_models_with_feedback

# Force retraining even with low feedback count
result = retrain_models_with_feedback.delay(force=True)
print(result.get())
```

### Production Mode

**Start Celery Beat (Scheduler):**
```bash
celery -A app.celery_config.celery_app beat --loglevel=info
```

**Start Celery Workers:**
```bash
# Workers handle both scans and retraining
celery -A app.celery_config.celery_app worker --loglevel=info --queues=celery,scan,training
```

**Scheduled Tasks:**
- `retrain_models_with_feedback`: Daily at 2 AM
- `cleanup_stale_scans`: Every 5 minutes

## Configuration

Environment variables:

```env
# Minimum feedback before retraining
MIN_FEEDBACK_THRESHOLD=50

# Retraining schedule (Cron-like)
RETRAIN_SCHEDULE=0 2 * * *  # 2 AM daily

# Model backup retention
MODEL_BACKUP_DAYS=30
```

## Monitoring

**Check Feedback Queue:**
```bash
# Count untrained feedback
redis-cli
> LLEN ai_feedback_untrained
```

**View Model Versions:**
```bash
ls -la backend/app/ai/models/
# network_model.pkl -> network_model_20240115_020000.pkl
```

**Retraining Logs:**
```
[Celery Task] Starting model retraining process
[Celery Task] 150 untrained feedback records found
[Celery Task] Backing up existing models to backup_20240115_020000
[Celery Task] Retraining network model with 50 feedback records
[Celery Task] Network model accuracy: 0.92 (improved from 0.89)
[Celery Task] Marking 50 feedback records as trained
[Celery Task] Retraining completed: model_version=20240115_020000
```

## Database Migration

Create the feedback table:

```bash
cd /home/andu/AI_Baseline_Assessment_Scanner/backend
flask db migrate -m "Add ai_feedback table for adaptive learning"
flask db upgrade
```

## Summary

The adaptive learning system transforms the security scanner from a static tool into an intelligent system that:

1. **Captures** analyst corrections
2. **Stores** feedback with metadata
3. **Retrains** models incrementally
4. **Deploys** updates safely
5. **Improves** accuracy over time

This creates a positive feedback loop where the AI becomes more accurate for your specific environment with every analyst review.

**Result:** A security scanner that gets smarter every day.
