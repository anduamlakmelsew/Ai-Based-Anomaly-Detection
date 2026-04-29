"""
network_pipeline.py

Production-grade network intrusion detection inference pipeline.
Supports both binary (Normal vs Attack) and multi-class (DoS, Probe, R2L, U2R, Normal) predictions.

Integration with trained models:
- network_model_binary.pkl / network_model_binary_xgb.pkl
- network_model_multiclass.pkl / network_model_multiclass_xgb.pkl
"""

import os
import json
import logging
from typing import Dict, List, Optional, Tuple
import numpy as np
import pandas as pd
import joblib

logger = logging.getLogger(__name__)

# Model paths
MODEL_DIR = os.path.dirname(os.path.abspath(__file__))
MODELS_PATH = os.path.join(MODEL_DIR, "models")

# Model file paths
BINARY_RF_PATH = os.path.join(MODELS_PATH, "network_model_binary.pkl")
BINARY_XGB_PATH = os.path.join(MODELS_PATH, "network_model_binary_xgb.pkl")
MULTI_RF_PATH = os.path.join(MODELS_PATH, "network_model_multiclass.pkl")
MULTI_XGB_PATH = os.path.join(MODELS_PATH, "network_model_multiclass_xgb.pkl")
PREPROCESSOR_PATH = os.path.join(MODELS_PATH, "network_preprocessor.pkl")
FEATURE_ENG_PATH = os.path.join(MODELS_PATH, "network_feature_engineer.pkl")
METADATA_PATH = os.path.join(MODELS_PATH, "network_model_metadata.json")

# Legacy model path (backward compatibility)
LEGACY_MODEL_PATH = os.path.join(MODELS_PATH, "network_model.pkl")

# Cached models
_model_cache = {}

# Multi-class category names
MULTICLASS_NAMES = ['Normal', 'DoS', 'Probe', 'R2L', 'U2R', 'Other']


def load_model(path: str, model_name: str) -> Optional[object]:
    """Load a model with error handling."""
    try:
        if not os.path.exists(path):
            logger.warning(f"{model_name} not found at: {path}")
            return None
        
        model = joblib.load(path)
        logger.info(f"Loaded {model_name} from {path}")
        return model
    except Exception as e:
        logger.error(f"Failed to load {model_name}: {e}")
        return None


def get_binary_model(prefer_xgb: bool = True) -> Optional[object]:
    """Get binary classification model (Normal vs Attack)."""
    cache_key = 'binary_xgb' if prefer_xgb else 'binary_rf'
    
    if cache_key not in _model_cache:
        # Try preferred model first
        if prefer_xgb and os.path.exists(BINARY_XGB_PATH):
            model = load_model(BINARY_XGB_PATH, "binary_xgb")
            if model:
                _model_cache[cache_key] = model
        elif not prefer_xgb and os.path.exists(BINARY_RF_PATH):
            model = load_model(BINARY_RF_PATH, "binary_rf")
            if model:
                _model_cache[cache_key] = model
        
        # Fallback
        if cache_key not in _model_cache:
            fallback_path = BINARY_RF_PATH if prefer_xgb else BINARY_XGB_PATH
            fallback_name = "binary_rf" if prefer_xgb else "binary_xgb"
            if os.path.exists(fallback_path):
                model = load_model(fallback_path, fallback_name)
                if model:
                    _model_cache[cache_key] = model
        
        # Legacy fallback
        if cache_key not in _model_cache and os.path.exists(LEGACY_MODEL_PATH):
            model = load_model(LEGACY_MODEL_PATH, "legacy_binary")
            if model:
                _model_cache[cache_key] = model
    
    return _model_cache.get(cache_key)


def get_multiclass_model(prefer_xgb: bool = True) -> Optional[object]:
    """Get multi-class classification model (DoS, Probe, R2L, U2R, Normal)."""
    cache_key = 'multiclass_xgb' if prefer_xgb else 'multiclass_rf'
    
    if cache_key not in _model_cache:
        # Try preferred model first
        if prefer_xgb and os.path.exists(MULTI_XGB_PATH):
            model = load_model(MULTI_XGB_PATH, "multiclass_xgb")
            if model:
                _model_cache[cache_key] = model
        elif not prefer_xgb and os.path.exists(MULTI_RF_PATH):
            model = load_model(MULTI_RF_PATH, "multiclass_rf")
            if model:
                _model_cache[cache_key] = model
        
        # Fallback
        if cache_key not in _model_cache:
            fallback_path = MULTI_RF_PATH if prefer_xgb else MULTI_XGB_PATH
            fallback_name = "multiclass_rf" if prefer_xgb else "multiclass_xgb"
            if os.path.exists(fallback_path):
                model = load_model(fallback_path, fallback_name)
                if model:
                    _model_cache[cache_key] = model
    
    return _model_cache.get(cache_key)


def get_preprocessor() -> Optional[object]:
    """Get feature preprocessor for scaling."""
    if 'preprocessor' not in _model_cache:
        if os.path.exists(PREPROCESSOR_PATH):
            preprocessor = load_model(PREPROCESSOR_PATH, "preprocessor")
            if preprocessor:
                _model_cache['preprocessor'] = preprocessor
    return _model_cache.get('preprocessor')


def extract_network_features_v2(scan_result: Dict) -> pd.DataFrame:
    """
    Extract comprehensive network features from scan result for new models.
    Creates engineered features matching the training pipeline.
    
    Args:
        scan_result: Network scan result dictionary
        
    Returns:
        DataFrame with engineered features (single row)
    """
    # Get raw metrics
    raw_metrics = scan_result.get("raw_metrics", {})
    services = scan_result.get("services", [])
    target = scan_result.get("target", "0.0.0.0")
    
    # Initialize features dict with all engineered features
    features = {}
    
    # =====================================================
    # FLOW FEATURES
    # =====================================================
    features['duration'] = raw_metrics.get('duration_seconds', 0)
    
    # Bytes estimation from services if not provided
    src_bytes = raw_metrics.get('src_bytes', 0)
    dst_bytes = raw_metrics.get('dst_bytes', 0)
    
    if src_bytes == 0 and dst_bytes == 0 and services:
        # Estimate from service types
        for svc in services:
            port = svc.get('port', 0)
            if port in [80, 443, 8080, 8443]:  # Web
                src_bytes += 1000
                dst_bytes += 2000
            elif port == 22:  # SSH
                src_bytes += 500
                dst_bytes += 800
            elif port in [21, 23]:  # FTP, Telnet
                src_bytes += 300
                dst_bytes += 400
            elif port == 53:  # DNS
                src_bytes += 100
                dst_bytes += 200
            elif port == 25:  # SMTP
                src_bytes += 400
                dst_bytes += 600
            elif port == 3306:  # MySQL
                src_bytes += 600
                dst_bytes += 1000
            else:
                src_bytes += 200
                dst_bytes += 300
    
    features['src_bytes'] = float(src_bytes)
    features['dst_bytes'] = float(dst_bytes)
    features['total_bytes'] = features['src_bytes'] + features['dst_bytes']
    
    # Packet counts (estimate from bytes/typical MTU of 1500)
    mtu = 1500
    features['src_packets'] = max(1, features['src_bytes'] / mtu)
    features['dst_packets'] = max(1, features['dst_bytes'] / mtu)
    features['packet_count'] = features['src_packets'] + features['dst_packets']
    
    # Rate features
    if features['duration'] > 0:
        features['bytes_per_second'] = features['total_bytes'] / features['duration']
        features['packets_per_second'] = features['packet_count'] / features['duration']
    else:
        features['bytes_per_second'] = 0
        features['packets_per_second'] = 0
    
    features['avg_packet_size'] = features['total_bytes'] / features['packet_count'] if features['packet_count'] > 0 else 0
    
    # =====================================================
    # STATISTICAL FEATURES (estimates)
    # =====================================================
    features['packet_size_mean'] = features['avg_packet_size']
    features['packet_size_std'] = features['packet_size_mean'] * 0.3 if features['packet_count'] > 1 else 0
    features['packet_size_min'] = features['packet_size_mean'] * 0.5
    features['packet_size_max'] = features['packet_size_mean'] * 1.5
    
    if features['packet_count'] > 1:
        features['inter_arrival_time_mean'] = features['duration'] / (features['packet_count'] - 1)
    else:
        features['inter_arrival_time_mean'] = 0
    features['inter_arrival_time_std'] = features['inter_arrival_time_mean'] * 0.5
    
    # =====================================================
    # BEHAVIORAL FEATURES
    # =====================================================
    features['connection_count'] = len(services) if services else 1
    features['unique_dst_ips'] = 1  # Single target
    features['unique_dst_ports'] = len(services) if services else 1
    
    features['same_src_ip_rate'] = 1.0
    features['same_dst_ip_rate'] = 1.0
    
    # Failed/successful connection estimates
    features['failed_connections'] = sum(1 for s in services if s.get('state') == 'closed')
    features['successful_connections'] = sum(1 for s in services if s.get('state') == 'open')
    
    if features['connection_count'] > 0:
        features['connection_success_rate'] = features['successful_connections'] / features['connection_count']
    else:
        features['connection_success_rate'] = 0.5
    
    # =====================================================
    # TCP FLAG FEATURES (estimates based on service state)
    # =====================================================
    open_count = sum(1 for s in services if s.get('state') == 'open')
    closed_count = sum(1 for s in services if s.get('state') == 'closed')
    
    features['syn_flag_count'] = len(services)  # SYN sent for each port
    features['ack_flag_count'] = open_count  # ACK for open ports
    features['rst_flag_count'] = closed_count  # RST for closed ports
    features['fin_flag_count'] = 0  # Unknown
    
    if features['ack_flag_count'] > 0:
        features['syn_to_ack_ratio'] = features['syn_flag_count'] / features['ack_flag_count']
    else:
        features['syn_to_ack_ratio'] = features['syn_flag_count']
    features['syn_to_ack_ratio'] = min(features['syn_to_ack_ratio'], 10)  # Cap at 10
    
    flag_total = features['syn_flag_count'] + features['ack_flag_count'] + features['rst_flag_count'] + features['fin_flag_count']
    features['rst_to_total_ratio'] = features['rst_flag_count'] / max(flag_total, 1)
    
    # =====================================================
    # TIME-BASED FEATURES
    # =====================================================
    features['connections_last_1s'] = features['connection_count']
    features['connections_last_10s'] = features['connection_count']
    features['connections_last_60s'] = features['connection_count']
    
    features['bytes_last_10s'] = features['total_bytes']
    features['packets_last_10s'] = features['packet_count']
    
    features['request_rate'] = features['packets_per_second']
    features['burst_rate'] = features['bytes_per_second'] / 1000  # KB/s
    features['time_since_last_connection'] = features['inter_arrival_time_mean']
    
    # =====================================================
    # PROTOCOL FEATURES (one-hot encoded)
    # =====================================================
    protocols = [s.get('protocol', 'tcp').lower() for s in services] if services else ['tcp']
    protocol_counts = {}
    for p in protocols:
        protocol_counts[p] = protocol_counts.get(p, 0) + 1
    
    dominant_protocol = max(protocol_counts, key=protocol_counts.get) if protocol_counts else 'tcp'
    
    features['protocol_tcp'] = 1 if dominant_protocol == 'tcp' else 0
    features['protocol_udp'] = 1 if dominant_protocol == 'udp' else 0
    features['protocol_icmp'] = 1 if dominant_protocol == 'icmp' else 0
    
    # =====================================================
    # SERVICE FEATURES (one-hot encoded)
    # =====================================================
    def infer_service(port):
        service_map = {
            80: 'http', 443: 'https', 8080: 'http', 8443: 'https',
            22: 'ssh', 21: 'ftp', 23: 'telnet', 25: 'smtp',
            53: 'dns', 110: 'pop3', 143: 'imap', 123: 'ntp',
            3306: 'mysql', 5432: 'postgresql', 1433: 'mssql',
            27017: 'mongodb', 6379: 'redis', 9200: 'elasticsearch',
        }
        return service_map.get(int(port), 'unknown')
    
    services_list = [infer_service(s.get('port', 0)).lower() for s in services] if services else ['unknown']
    
    features['service_http'] = 1 if 'http' in services_list else 0
    features['service_https'] = 1 if 'https' in services_list else 0
    features['service_ssh'] = 1 if 'ssh' in services_list else 0
    features['service_ftp'] = 1 if 'ftp' in services_list else 0
    features['service_dns'] = 1 if 'dns' in services_list else 0
    features['service_smtp'] = 1 if 'smtp' in services_list else 0
    features['service_other'] = 1 if all(s not in services_list for s in ['http', 'https', 'ssh', 'ftp', 'dns', 'smtp']) else 0
    
    # =====================================================
    # FLAG FEATURES (one-hot encoded)
    # =====================================================
    open_services = sum(1 for s in services if s.get('state') == 'open')
    closed_services = sum(1 for s in services if s.get('state') == 'closed')
    
    features['flag_sf'] = 1 if open_services > 0 else 0  # SYN-FIN (successful)
    features['flag_rej'] = 1 if closed_services > closed_services // 2 else 0  # Rejected
    features['flag_s0'] = 1 if closed_services > open_services else 0  # SYN only
    features['flag_other'] = 0
    
    # =====================================================
    # PORT-BASED FEATURES
    # =====================================================
    ports = [s.get('port', 0) for s in services] if services else [0]
    dst_port = ports[0] if ports else 0
    
    features['is_well_known_port'] = 1 if dst_port <= 1023 else 0
    features['is_registered_port'] = 1 if 1024 <= dst_port <= 49151 else 0
    features['is_dynamic_port'] = 1 if dst_port > 49151 else 0
    features['port_entropy'] = len(set(ports))  # Unique port count
    
    # Clip all features to avoid infinities
    for key in features:
        val = features[key]
        if isinstance(val, (int, float)):
            if np.isinf(val) or np.isnan(val):
                features[key] = 0
            else:
                features[key] = float(np.clip(val, -1e9, 1e9))
    
    # Create DataFrame
    df = pd.DataFrame([features])
    
    return df


def extract_network_features(scan_result):
    """
    Legacy feature extraction for backward compatibility.
    Extracts basic 6 features for old models.
    """
    features = {}
    raw_metrics = scan_result.get("raw_metrics", {})
    services = scan_result.get("services", [])

    features["duration"] = raw_metrics.get("duration_seconds", 0)

    # Byte counts
    estimated_src_bytes = 0
    estimated_dst_bytes = 0

    for svc in services:
        port = svc.get("port", 0)
        if port in [80, 443, 8080]:
            estimated_src_bytes += 1000
            estimated_dst_bytes += 2000
        elif port == 22:
            estimated_src_bytes += 500
            estimated_dst_bytes += 800
        elif port in [21, 23]:
            estimated_src_bytes += 300
            estimated_dst_bytes += 400
        else:
            estimated_src_bytes += 200
            estimated_dst_bytes += 300

    features["src_bytes"] = raw_metrics.get("src_bytes", estimated_src_bytes)
    features["dst_bytes"] = raw_metrics.get("dst_bytes", estimated_dst_bytes)

    # Protocol distribution
    protocol_counts = {"icmp": 0, "tcp": 0, "udp": 0}
    for svc in services:
        protocol = svc.get("protocol", "tcp").lower()
        if protocol in protocol_counts:
            protocol_counts[protocol] += 1

    features["protocol_icmp"] = 1 if protocol_counts["icmp"] > 0 else 0
    features["protocol_tcp"] = 1 if protocol_counts["tcp"] > 0 else 0
    features["protocol_udp"] = 1 if protocol_counts["udp"] > 0 else 0

    return features


def analyze_network_binary(scan_result: Dict, prefer_xgb: bool = True) -> Dict:
    """
    Run binary classification analysis (Normal vs Attack).
    
    Args:
        scan_result: Network scan result dictionary
        prefer_xgb: Prefer XGBoost over RandomForest if available
        
    Returns:
        Dict with prediction results
    """
    model = get_binary_model(prefer_xgb=prefer_xgb)
    
    if model is None:
        # Fallback to legacy analysis
        logger.warning("New binary models not available, falling back to legacy")
        return analyze_network_legacy(scan_result)
    
    try:
        # Extract features using new pipeline
        features_df = extract_network_features_v2(scan_result)
        
        # Apply preprocessing if available
        preprocessor = get_preprocessor()
        if preprocessor:
            try:
                features_scaled = preprocessor.transform(features_df)
            except Exception as e:
                logger.warning(f"Preprocessor failed, using raw features: {e}")
                features_scaled = features_df.values
        else:
            features_scaled = features_df.values
        
        # Run prediction
        prediction = model.predict(features_scaled)[0]
        
        # Get probability
        if hasattr(model, "predict_proba"):
            probabilities = model.predict_proba(features_scaled)[0]
            confidence = float(max(probabilities))
            attack_probability = float(probabilities[1]) if len(probabilities) > 1 else confidence
        else:
            confidence = 1.0
            attack_probability = float(prediction)
        
        # Map prediction
        prediction_label = "attack" if prediction == 1 else "normal"
        
        return {
            "prediction": prediction_label,
            "confidence": round(confidence, 4),
            "attack_probability": round(attack_probability, 4),
            "is_attack": bool(prediction == 1),
            "model_type": "xgboost" if prefer_xgb and os.path.exists(BINARY_XGB_PATH) else "random_forest",
            "classification_type": "binary",
            "features_summary": {
                "duration": float(features_df['duration'].iloc[0]),
                "total_bytes": float(features_df['total_bytes'].iloc[0]),
                "packet_count": float(features_df['packet_count'].iloc[0]),
                "connection_count": float(features_df['connection_count'].iloc[0]),
            }
        }
        
    except Exception as e:
        logger.error(f"Binary analysis failed: {str(e)}")
        return {
            "error": str(e),
            "prediction": "error",
            "confidence": 0.0,
            "is_attack": False,
            "classification_type": "binary"
        }


def analyze_network_multiclass(scan_result: Dict, prefer_xgb: bool = True) -> Dict:
    """
    Run multi-class classification analysis (DoS, Probe, R2L, U2R, Normal).
    
    Args:
        scan_result: Network scan result dictionary
        prefer_xgb: Prefer XGBoost over RandomForest if available
        
    Returns:
        Dict with prediction results including attack category
    """
    model = get_multiclass_model(prefer_xgb=prefer_xgb)
    
    if model is None:
        logger.warning("Multi-class model not available")
        return {
            "error": "Multi-class model not available",
            "prediction": "unknown",
            "confidence": 0.0,
            "classification_type": "multiclass"
        }
    
    try:
        # Extract features using new pipeline
        features_df = extract_network_features_v2(scan_result)
        
        # Apply preprocessing if available
        preprocessor = get_preprocessor()
        if preprocessor:
            try:
                features_scaled = preprocessor.transform(features_df)
            except Exception as e:
                logger.warning(f"Preprocessor failed, using raw features: {e}")
                features_scaled = features_df.values
        else:
            features_scaled = features_df.values
        
        # Run prediction
        prediction = model.predict(features_scaled)[0]
        
        # Get probability distribution
        if hasattr(model, "predict_proba"):
            probabilities = model.predict_proba(features_scaled)[0]
            confidence = float(max(probabilities))
            
            # Top 3 predictions
            top_indices = np.argsort(probabilities)[-3:][::-1]
            top_predictions = [
                {
                    "category": MULTICLASS_NAMES[idx] if idx < len(MULTICLASS_NAMES) else f"Class_{idx}",
                    "probability": round(float(probabilities[idx]), 4)
                }
                for idx in top_indices
            ]
        else:
            confidence = 1.0
            top_predictions = []
        
        # Map prediction to category name
        category_index = int(prediction)
        category_name = MULTICLASS_NAMES[category_index] if category_index < len(MULTICLASS_NAMES) else f"Class_{category_index}"
        
        is_attack = category_index != 0  # 0 is Normal
        
        return {
            "prediction": category_name.lower(),
            "category": category_name,
            "confidence": round(confidence, 4),
            "is_attack": is_attack,
            "attack_type": category_name if is_attack else None,
            "top_predictions": top_predictions,
            "model_type": "xgboost" if prefer_xgb and os.path.exists(MULTI_XGB_PATH) else "random_forest",
            "classification_type": "multiclass",
            "features_summary": {
                "duration": float(features_df['duration'].iloc[0]),
                "total_bytes": float(features_df['total_bytes'].iloc[0]),
                "packet_count": float(features_df['packet_count'].iloc[0]),
                "connection_count": float(features_df['connection_count'].iloc[0]),
            }
        }
        
    except Exception as e:
        logger.error(f"Multi-class analysis failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return {
            "error": str(e),
            "prediction": "error",
            "confidence": 0.0,
            "classification_type": "multiclass"
        }


def analyze_network_legacy(scan_result):
    """
    Legacy analysis function for backward compatibility.
    Uses old 6-feature model if available.
    """
    from .loader import get_network_model
    
    model = get_network_model()
    if model is None:
        return {
            "error": "Network model not available",
            "prediction": "unknown",
            "confidence": 0.0
        }

    try:
        features = extract_network_features(scan_result)
        feature_df = pd.DataFrame([features])
        
        expected_features = [
            "duration", "src_bytes", "dst_bytes",
            "protocol_icmp", "protocol_tcp", "protocol_udp"
        ]
        feature_df = feature_df[expected_features]

        prediction = model.predict(feature_df)[0]

        if hasattr(model, "predict_proba"):
            probabilities = model.predict_proba(feature_df)[0]
            confidence = float(max(probabilities))
        else:
            confidence = 1.0

        prediction_label = "anomaly" if prediction == 1 else "normal"

        return {
            "prediction": prediction_label,
            "confidence": round(confidence, 3),
            "features_used": features,
            "model_type": "legacy_random_forest",
            "classification_type": "binary"
        }

    except Exception as e:
        logger.error(f"Legacy network AI analysis failed: {str(e)}")
        return {
            "error": str(e),
            "prediction": "error",
            "confidence": 0.0
        }


def analyze_network(scan_result):
    """
    Main entry point for network AI analysis.
    Runs both binary and multi-class analysis if available.
    
    Args:
        scan_result: Network scan result dictionary
        
    Returns:
        Dict with comprehensive prediction results
    """
    logger.info("Running network AI analysis")
    
    results = {
        "timestamp": pd.Timestamp.now().isoformat(),
        "target": scan_result.get("target", "unknown"),
    }
    
    # Run binary classification
    binary_result = analyze_network_binary(scan_result, prefer_xgb=True)
    results["binary"] = binary_result
    
    # Run multi-class classification if attack detected or available
    if binary_result.get("is_attack", False) or os.path.exists(MULTI_RF_PATH) or os.path.exists(MULTI_XGB_PATH):
        multiclass_result = analyze_network_multiclass(scan_result, prefer_xgb=True)
        results["multiclass"] = multiclass_result
        
        # Add primary prediction for backward compatibility
        if "error" not in multiclass_result:
            results["prediction"] = multiclass_result["prediction"]
            results["confidence"] = multiclass_result["confidence"]
            results["attack_type"] = multiclass_result.get("attack_type")
        else:
            results["prediction"] = binary_result["prediction"]
            results["confidence"] = binary_result["confidence"]
    else:
        # Only binary available
        results["prediction"] = binary_result["prediction"]
        results["confidence"] = binary_result["confidence"]
    
    # Add model availability info
    results["models_available"] = {
        "binary_rf": os.path.exists(BINARY_RF_PATH),
        "binary_xgb": os.path.exists(BINARY_XGB_PATH),
        "multiclass_rf": os.path.exists(MULTI_RF_PATH),
        "multiclass_xgb": os.path.exists(MULTI_XGB_PATH),
    }
    
    return results


def clear_model_cache():
    """Clear the model cache (useful for testing or reloading)."""
    global _model_cache
    _model_cache = {}
    logger.info("Model cache cleared")


# Export symbols
__all__ = [
    'analyze_network',
    'analyze_network_binary',
    'analyze_network_multiclass',
    'analyze_network_legacy',
    'extract_network_features',
    'extract_network_features_v2',
    'clear_model_cache',
    'get_binary_model',
    'get_multiclass_model',
]
