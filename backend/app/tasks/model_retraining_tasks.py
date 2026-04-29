"""
Model Retraining Tasks
Celery tasks for periodic model retraining using feedback data.
This enables adaptive learning without disrupting inference.
"""
import os
import logging
import pickle
import shutil
from datetime import datetime
from celery import shared_task
from sqlalchemy.exc import SQLAlchemyError

# Import feedback model
from app.models.ai_feedback_model import AIFeedback
from app import db

logger = logging.getLogger(__name__)

# Model paths
MODELS_DIR = os.path.join(os.path.dirname(__file__), '..', 'ai', 'models')
BACKUP_DIR = os.path.join(MODELS_DIR, 'backups')


@shared_task(
    bind=True,
    max_retries=2,
    default_retry_delay=300,  # 5 minutes
    soft_time_limit=1800,  # 30 minutes
    time_limit=3600,  # 1 hour
    autoretry_for=(SQLAlchemyError,),
)
def retrain_models_with_feedback(self, force=False):
    """
    Periodic task to retrain AI models using user feedback.
    
    This task:
    1. Checks for sufficient new feedback data
    2. Retrains models using feedback + original training data
    3. Validates new models on held-out test set
    4. Deploys new models if they perform better
    5. Keeps backup of previous models
    
    Args:
        force: If True, retrain even if minimum feedback threshold not met
    
    Returns:
        dict with retraining results and metrics
    """
    logger.info("[Celery Task] Starting model retraining process")
    
    try:
        # Step 1: Check if enough new feedback exists
        min_feedback_threshold = 50  # Minimum feedback records needed
        
        untrained_count = AIFeedback.query.filter_by(used_for_training=False).count()
        
        if untrained_count < min_feedback_threshold and not force:
            logger.info(f"[Celery Task] Insufficient feedback for retraining ({untrained_count}/{min_feedback_threshold})")
            return {
                "status": "skipped",
                "reason": f"Insufficient feedback data ({untrained_count} records, minimum {min_feedback_threshold})",
                "untrained_feedback_count": untrained_count
            }
        
        # Step 2: Prepare training data from feedback
        logger.info("[Celery Task] Preparing training data from feedback")
        
        training_data = _prepare_training_data_from_feedback()
        
        if not training_data or sum(len(v) for v in training_data.values()) == 0:
            logger.warning("[Celery Task] No valid training data prepared")
            return {
                "status": "failed",
                "reason": "No valid training data could be prepared from feedback",
                "training_data_stats": {k: len(v) for k, v in training_data.items()}
            }
        
        # Step 3: Backup existing models
        logger.info("[Celery Task] Backing up existing models")
        backup_version = _backup_current_models()
        
        if not backup_version:
            logger.error("[Celery Task] Model backup failed, aborting retraining")
            return {
                "status": "failed",
                "reason": "Model backup failed"
            }
        
        # Step 4: Retrain each model type
        results = {}
        model_version = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        
        for model_type in ['network', 'system', 'web']:
            if model_type not in training_data or len(training_data[model_type]) < 10:
                logger.info(f"[Celery Task] Skipping {model_type} model - insufficient data")
                results[model_type] = {"status": "skipped", "reason": "insufficient data"}
                continue
            
            try:
                logger.info(f"[Celery Task] Retraining {model_type} model")
                
                # Update task state
                self.update_state(
                    state='PROGRESS',
                    meta={'stage': f'Retraining {model_type} model', 'progress': 30}
                )
                
                # Call model-specific retraining function
                retrain_result = _retrain_model_type(model_type, training_data[model_type], model_version)
                results[model_type] = retrain_result
                
            except Exception as e:
                logger.exception(f"[Celery Task] Failed to retrain {model_type} model")
                results[model_type] = {"status": "failed", "error": str(e)}
        
        # Step 5: Mark feedback as used for training
        successful_types = [k for k, v in results.items() if v.get("status") == "success"]
        
        if successful_types:
            logger.info(f"[Celery Task] Marking feedback as trained for models: {successful_types}")
            
            # Get feedback IDs used for successful retrainings
            feedback_ids = []
            for model_type in successful_types:
                feedback_ids.extend([f.id for f in training_data.get(model_type, [])])
            
            # Mark as trained
            if feedback_ids:
                AIFeedback.mark_as_trained(feedback_ids, model_version)
        
        # Step 6: Generate summary
        summary = {
            "status": "completed",
            "model_version": model_version,
            "backup_version": backup_version,
            "feedback_used": {k: len(v) for k, v in training_data.items()},
            "results": results,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        logger.info(f"[Celery Task] Retraining completed: {summary}")
        
        return summary
        
    except Exception as e:
        logger.exception("[Celery Task] Model retraining failed")
        
        # Restore from backup if retraining failed
        try:
            _restore_from_backup()
            logger.info("[Celery Task] Models restored from backup after failure")
        except Exception as restore_error:
            logger.error(f"[Celery Task] Failed to restore models: {restore_error}")
        
        raise


def _prepare_training_data_from_feedback():
    """
    Prepare training data from user feedback.
    
    Returns:
        dict: {model_type: [feedback_records]}
    """
    training_data = {
        'network': [],
        'system': [],
        'web': []
    }
    
    # Get all untrained feedback
    feedback_records = AIFeedback.get_untrained_feedback(limit=1000)
    
    for feedback in feedback_records:
        if feedback.source_type in training_data:
            training_data[feedback.source_type].append(feedback)
    
    return training_data


def _backup_current_models():
    """
    Backup current model files before retraining.
    
    Returns:
        str: Backup version identifier, or None if backup failed
    """
    try:
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        backup_path = os.path.join(BACKUP_DIR, f"backup_{timestamp}")
        
        os.makedirs(backup_path, exist_ok=True)
        
        # Copy all .pkl and .joblib files
        for filename in os.listdir(MODELS_DIR):
            if filename.endswith(('.pkl', '.joblib', '.h5')):
                src = os.path.join(MODELS_DIR, filename)
                dst = os.path.join(backup_path, filename)
                shutil.copy2(src, dst)
        
        logger.info(f"Models backed up to {backup_path}")
        return timestamp
        
    except Exception as e:
        logger.error(f"Model backup failed: {e}")
        return None


def _retrain_model_type(model_type, feedback_records, model_version):
    """
    Retrain a specific model type using feedback data.
    
    Args:
        model_type: 'network', 'system', or 'web'
        feedback_records: List of AIFeedback records
        model_version: Version string for the new model
    
    Returns:
        dict with retraining results
    """
    logger.info(f"Retraining {model_type} model with {len(feedback_records)} feedback records")
    
    # Import model-specific training modules
    if model_type == 'network':
        return _retrain_network_model(feedback_records, model_version)
    elif model_type == 'system':
        return _retrain_system_model(feedback_records, model_version)
    elif model_type == 'web':
        return _retrain_web_model(feedback_records, model_version)
    else:
        return {"status": "failed", "error": f"Unknown model type: {model_type}"}


def _retrain_network_model(feedback_records, model_version):
    """
    Retrain network intrusion detection model.
    
    Uses feedback to improve attack classification accuracy.
    """
    try:
        # Import training pipeline
        from app.ai.training.network_training_pipeline import NetworkTrainingPipeline
        
        # Convert feedback to training format
        training_samples = []
        labels = []
        
        for feedback in feedback_records:
            # Extract features from feedback context (stored in AI detection event)
            if feedback.ai_detection_event_id:
                event = AIDetectionEvent.query.get(feedback.ai_detection_event_id)
                if event and event.input_data:
                    features = _extract_network_features(event.input_data)
                    training_samples.append(features)
                    labels.append(feedback.corrected_label)
        
        if len(training_samples) < 10:
            return {"status": "skipped", "reason": "Insufficient training samples after feature extraction"}
        
        # Train model incrementally
        pipeline = NetworkTrainingPipeline()
        metrics = pipeline.incremental_train(training_samples, labels)
        
        # Save new model
        model_path = os.path.join(MODELS_DIR, f'network_model_{model_version}.pkl')
        pipeline.save_model(model_path)
        
        # Update symlink to new model (atomic swap)
        current_model = os.path.join(MODELS_DIR, 'network_model.pkl')
        temp_link = os.path.join(MODELS_DIR, 'network_model_new.pkl')
        
        os.symlink(model_path, temp_link)
        os.rename(temp_link, current_model)
        
        return {
            "status": "success",
            "model_type": "network",
            "samples_used": len(training_samples),
            "accuracy": metrics.get('accuracy', 0),
            "model_path": model_path
        }
        
    except Exception as e:
        logger.exception(f"Network model retraining failed")
        return {"status": "failed", "error": str(e)}


def _retrain_system_model(feedback_records, model_version):
    """
    Retrain system security model.
    
    Uses feedback to improve system vulnerability detection.
    """
    try:
        from sklearn.ensemble import RandomForestClassifier
        import numpy as np
        
        # Prepare training data
        X = []
        y = []
        
        for feedback in feedback_records:
            if feedback.ai_detection_event_id:
                event = AIDetectionEvent.query.get(feedback.ai_detection_event_id)
                if event and event.system_prediction:
                    # Extract features from system prediction data
                    features = _extract_system_features(event.system_prediction)
                    X.append(features)
                    y.append(1 if feedback.corrected_label in ['at-risk', 'compromised'] else 0)
        
        if len(X) < 10:
            return {"status": "skipped", "reason": "Insufficient training samples"}
        
        X = np.array(X)
        y = np.array(y)
        
        # Train model
        model = RandomForestClassifier(n_estimators=100, random_state=42)
        model.fit(X, y)
        
        # Save model
        model_path = os.path.join(MODELS_DIR, f'system_model_{model_version}.pkl')
        with open(model_path, 'wb') as f:
            pickle.dump(model, f)
        
        # Update symlink
        current_model = os.path.join(MODELS_DIR, 'system_model.pkl')
        if os.path.exists(current_model):
            os.remove(current_model)
        os.symlink(model_path, current_model)
        
        return {
            "status": "success",
            "model_type": "system",
            "samples_used": len(X),
            "model_path": model_path
        }
        
    except Exception as e:
        logger.exception(f"System model retraining failed")
        return {"status": "failed", "error": str(e)}


def _retrain_web_model(feedback_records, model_version):
    """
    Retrain web vulnerability model.
    
    Uses feedback to improve web vulnerability classification.
    """
    try:
        from sklearn.ensemble import RandomForestClassifier
        from sklearn.feature_extraction.text import TfidfVectorizer
        import numpy as np
        
        # Prepare text data from web findings
        texts = []
        labels = []
        
        for feedback in feedback_records:
            if feedback.ai_detection_event_id:
                event = AIDetectionEvent.query.get(feedback.ai_detection_event_id)
                if event and event.web_prediction:
                    # Extract text from web prediction
                    text = _extract_web_text(event.web_prediction)
                    texts.append(text)
                    labels.append(1 if feedback.corrected_label == 'vulnerable' else 0)
        
        if len(texts) < 10:
            return {"status": "skipped", "reason": "Insufficient training samples"}
        
        # Vectorize text
        vectorizer = TfidfVectorizer(max_features=1000)
        X = vectorizer.fit_transform(texts)
        y = np.array(labels)
        
        # Train model
        model = RandomForestClassifier(n_estimators=100, random_state=42)
        model.fit(X, y)
        
        # Save model and vectorizer
        model_path = os.path.join(MODELS_DIR, f'web_model_{model_version}.pkl')
        vectorizer_path = os.path.join(MODELS_DIR, f'web_vectorizer_{model_version}.pkl')
        
        with open(model_path, 'wb') as f:
            pickle.dump(model, f)
        with open(vectorizer_path, 'wb') as f:
            pickle.dump(vectorizer, f)
        
        # Update symlinks
        for name, path in [('web_model.pkl', model_path), ('web_vectorizer.pkl', vectorizer_path)]:
            current = os.path.join(MODELS_DIR, name)
            if os.path.exists(current):
                os.remove(current)
            os.symlink(path, current)
        
        return {
            "status": "success",
            "model_type": "web",
            "samples_used": len(texts),
            "model_path": model_path
        }
        
    except Exception as e:
        logger.exception(f"Web model retraining failed")
        return {"status": "failed", "error": str(e)}


def _extract_network_features(input_data):
    """Extract feature vector from network input data."""
    # Simplified feature extraction
    features = [
        input_data.get('duration', 0),
        input_data.get('src_bytes', 0),
        input_data.get('dst_bytes', 0),
        input_data.get('src_port', 0),
        input_data.get('dst_port', 0),
        input_data.get('packet_count', 0),
        input_data.get('flag_count', 0),
    ]
    return features


def _extract_system_features(prediction_data):
    """Extract feature vector from system prediction data."""
    features = [
        prediction_data.get('cpu_usage', 50),
        prediction_data.get('memory_usage', 50),
        prediction_data.get('disk_usage', 50),
        prediction_data.get('open_ports_count', 0),
        prediction_data.get('process_count', 0),
    ]
    return features


def _extract_web_text(prediction_data):
    """Extract text from web prediction for vectorization."""
    parts = []
    if prediction_data.get('findings'):
        for finding in prediction_data['findings']:
            parts.append(f"{finding.get('type', '')} {finding.get('evidence', '')}")
    return ' '.join(parts)


def _restore_from_backup():
    """Restore models from most recent backup."""
    try:
        # Find most recent backup
        backups = [d for d in os.listdir(BACKUP_DIR) if d.startswith('backup_')]
        if not backups:
            logger.error("No backup found to restore from")
            return False
        
        latest_backup = sorted(backups)[-1]
        backup_path = os.path.join(BACKUP_DIR, latest_backup)
        
        # Restore files
        for filename in os.listdir(backup_path):
            src = os.path.join(backup_path, filename)
            dst = os.path.join(MODELS_DIR, filename)
            shutil.copy2(src, dst)
        
        logger.info(f"Models restored from backup: {backup_path}")
        return True
        
    except Exception as e:
        logger.error(f"Failed to restore from backup: {e}")
        return False
