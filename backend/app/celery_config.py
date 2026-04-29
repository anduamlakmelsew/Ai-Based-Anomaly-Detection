"""
Celery Configuration for Async Scan Processing

This module configures Celery with Redis as the message broker
to enable asynchronous background task processing for security scans.
"""

import os
import logging
from celery import Celery, Task
from celery.signals import task_prerun, task_postrun, task_failure

# Redis configuration from environment
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")

logger = logging.getLogger(__name__)

# Flask app reference (set by init_celery_app)
_flask_app = None


class ContextTask(Task):
    """
    Custom Celery Task class that runs tasks within Flask app context.
    
    This ensures database connections, config, and other Flask resources
    are available in worker processes.
    """
    abstract = True  # Don't register this as a concrete task
    
    def __call__(self, *args, **kwargs):
        if _flask_app is not None:
            with _flask_app.app_context():
                return self.run(*args, **kwargs)
        else:
            # Fallback: try to run without context (will fail if DB needed)
            logger.warning("Flask app context not initialized, running task without context")
            return self.run(*args, **kwargs)


# Create Celery app with custom task class
celery_app = Celery(
    "security_scanner",
    broker=REDIS_URL,
    backend=REDIS_URL,
    include=[
        "app.tasks.scan_tasks",  # Scan execution tasks
        "app.tasks.model_retraining_tasks",  # Model retraining tasks
    ],
    task_cls=ContextTask  # Use custom task class for all tasks
)

# Celery configuration
celery_app.conf.update(
    # Task execution
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    
    # Task execution settings
    task_always_eager=False,  # Set to True for testing without workers
    task_store_eager_result=True,
    task_track_started=True,  # Track when tasks start
    task_time_limit=3600,  # 1 hour max per task
    task_soft_time_limit=3300,  # Warn at 55 minutes
    
    # Result backend settings
    result_expires=86400,  # Results expire after 24 hours
    result_extended=True,
    
    # Worker settings
    worker_prefetch_multiplier=1,  # Don't prefetch tasks (good for long tasks)
    worker_max_tasks_per_child=50,  # Restart worker after 50 tasks
    
    # Retry settings
    task_default_retry_delay=60,  # Retry after 1 minute
    task_max_retries=3,  # Max 3 retries
    
    # Rate limiting
    task_annotations={
        "app.tasks.scan_tasks.run_security_scan": {
            "rate_limit": "10/m"  # Max 10 scans per minute per worker
        }
    },
    
    # Periodic task schedule (Celery Beat)
    beat_schedule={
        # Run model retraining daily at 2 AM (when system is less busy)
        'retrain-models-daily': {
            'task': 'app.tasks.model_retraining_tasks.retrain_models_with_feedback',
            'schedule': 86400.0,  # Every 24 hours (in seconds)
            'kwargs': {'force': False},  # Only retrain if enough new feedback
        },
        # Clean up stale scans every 5 minutes
        'cleanup-stale-scans': {
            'task': 'app.tasks.scan_tasks.cleanup_stale_scans',
            'schedule': 300.0,  # Every 5 minutes
        },
    },
    beat_max_loop_interval=300,  # Check schedule every 5 minutes
)


# Task lifecycle hooks for monitoring
@task_prerun.connect
def task_prerun_handler(sender=None, task_id=None, task=None, args=None, kwargs=None, **kw):
    """Called before task execution"""
    import logging
    logger = logging.getLogger(__name__)
    logger.info(f"Task {task.name}[{task_id}] starting with args: {args}, kwargs: {kwargs}")


@task_postrun.connect
def task_postrun_handler(sender=None, task_id=None, task=None, args=None, kwargs=None, retval=None, state=None, **kw):
    """Called after task execution"""
    import logging
    logger = logging.getLogger(__name__)
    logger.info(f"Task {task.name}[{task_id}] finished with state: {state}")


@task_failure.connect
def task_failure_handler(sender=None, task_id=None, exception=None, args=None, kwargs=None, traceback=None, einfo=None, **kw):
    """Called when task fails"""
    import logging
    logger = logging.getLogger(__name__)
    logger.error(f"Task [{task_id}] failed with exception: {exception}")


# Auto-discover tasks
celery_app.autodiscover_tasks()


def init_celery_app(flask_app):
    """
    Initialize Celery with Flask app context.
    
    Must be called during Flask app initialization to enable
    database access and other Flask resources in Celery workers.
    
    Args:
        flask_app: The Flask application instance
    
    Returns:
        Celery app instance
    """
    global _flask_app
    _flask_app = flask_app
    
    # Update Celery config from Flask config
    celery_app.conf.update(
        result_backend=flask_app.config.get('CELERY_RESULT_BACKEND', REDIS_URL),
        broker_url=flask_app.config.get('CELERY_BROKER_URL', REDIS_URL),
    )
    
    logger.info("Celery initialized with Flask app context")
    return celery_app
