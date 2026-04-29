"""
AI Model Loader - Safe model loading with error handling
"""
import os
import logging
import joblib

logger = logging.getLogger(__name__)

# Model paths
MODEL_DIR = os.path.dirname(os.path.abspath(__file__))
NETWORK_MODEL_PATH = os.path.join(MODEL_DIR, "models", "network_model.pkl")
WEB_MODEL_PATH = os.path.join(MODEL_DIR, "models", "web_model.pkl")
WEB_VECTORIZER_PATH = os.path.join(MODEL_DIR, "models", "web_vectorizer.pkl")
SYSTEM_MODEL_PATH = os.path.join(MODEL_DIR, "models", "system", "system_security_model.pkl")

# Cached models
_models = {}


def load_model(model_path, model_name="model"):
    """
    Load a pickled model with error handling.
    Returns None if model fails to load.
    """
    try:
        if not os.path.exists(model_path):
            logger.warning(f"{model_name} not found at: {model_path}")
            return None

        model = joblib.load(model_path)
        logger.info(f"Loaded {model_name} from {model_path}")
        return model

    except Exception as e:
        logger.error(f"Failed to load {model_name}: {str(e)}")
        return None


def get_network_model():
    """Get cached network model or load it."""
    if "network" not in _models:
        _models["network"] = load_model(NETWORK_MODEL_PATH, "network_model")
    return _models["network"]


def get_web_model():
    """Get cached web model or load it."""
    if "web" not in _models:
        _models["web"] = load_model(WEB_MODEL_PATH, "web_model")
    return _models["web"]


def get_web_vectorizer():
    """Get cached web vectorizer or load it."""
    if "web_vectorizer" not in _models:
        _models["web_vectorizer"] = load_model(WEB_VECTORIZER_PATH, "web_vectorizer")
    return _models["web_vectorizer"]


def get_system_model():
    """Get cached system security model or load it."""
    if "system" not in _models:
        _models["system"] = load_model(SYSTEM_MODEL_PATH, "system_security_model")
    return _models["system"]


def clear_cache():
    """Clear model cache (useful for testing)."""
    _models.clear()
