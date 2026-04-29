"""
unified_security_ml_service.py

Unified AI inference service for all security models.
Loads all models once at startup and provides prediction APIs.
"""

import os
import json
import logging
import joblib
import numpy as np
import pandas as pd
from typing import Dict, List, Optional, Any, Tuple, Set
from threading import Lock
from dataclasses import dataclass, asdict, field
from datetime import datetime, timezone

logger = logging.getLogger(__name__)

# =============================================================================
# INPUT SCHEMAS - Define required and optional fields for each model
# =============================================================================

NETWORK_SCHEMA = {
    "required": ["duration", "src_bytes", "dst_bytes", "protocol"],
    "optional": ["packet_count", "src_packets", "dst_packets", "total_bytes",
                 "src_port", "dst_port", "syn_flag", "ack_flag", "rst_flag", "fin_flag"],
    "defaults": {
        "duration": 0.0,
        "src_bytes": 0.0,
        "dst_bytes": 0.0,
        "total_bytes": 0.0,
        "packet_count": 0.0,
        "src_packets": 0.0,
        "dst_packets": 0.0,
        "protocol": "tcp",
        "src_port": 0,
        "dst_port": 80,
        "syn_flag": 0,
        "ack_flag": 0,
        "rst_flag": 0,
        "fin_flag": 0
    },
    "numeric_ranges": {
        "duration": (0.0, 1e6),
        "src_bytes": (0.0, 1e12),
        "dst_bytes": (0.0, 1e12),
        "packet_count": (0.0, 1e9),
        "src_port": (0, 65535),
        "dst_port": (0, 65535)
    }
}

SYSTEM_SCHEMA = {
    "required": ["cpu_usage", "memory_usage", "open_ports"],
    "optional": ["disk_usage", "process_count", "suspicious_processes", "user_count",
                 "admin_count", "service_count", "exposed_services", "total_vulns",
                 "critical_vulns", "high_vulns", "firewall_enabled"],
    "defaults": {
        "cpu_usage": 50.0,
        "memory_usage": 50.0,
        "disk_usage": 50.0,
        "open_ports": 0,
        "process_count": 100,
        "suspicious_processes": 0,
        "user_count": 1,
        "admin_count": 1,
        "service_count": 10,
        "exposed_services": 0,
        "total_vulns": 0,
        "critical_vulns": 0,
        "high_vulns": 0,
        "firewall_enabled": 1
    },
    "numeric_ranges": {
        "cpu_usage": (0.0, 100.0),
        "memory_usage": (0.0, 100.0),
        "disk_usage": (0.0, 100.0),
        "open_ports": (0, 65535),
        "process_count": (0, 100000),
        "suspicious_processes": (0, 1000)
    }
}

WEB_SCHEMA = {
    "required": [],  # Either payload, response, or url required
    "optional": ["payload", "response", "url", "method", "headers", "status_code"],
    "defaults": {
        "payload": "",
        "response": "",
        "url": "/",
        "method": "GET",
        "headers": {},
        "status_code": 200
    },
    "numeric_ranges": {
        "status_code": (100, 599)
    }
}

# =============================================================================
# VALIDATION AND NORMALIZATION UTILITIES
# =============================================================================

def validate_and_normalize_input(
    data: Optional[Dict[str, Any]],
    schema: Dict[str, Any],
    model_name: str
) -> Tuple[Dict[str, Any], List[str], List[str]]:
    """
    Validate and normalize input data against schema.
    
    Returns:
        Tuple of (normalized_data, missing_fields, warnings)
    """
    if data is None:
        logger.warning(f"[{model_name}] Received None input, applying all defaults")
        return schema["defaults"].copy(), list(schema["required"]), ["Input was None, using all defaults"]
    
    if not isinstance(data, dict):
        logger.error(f"[{model_name}] Invalid input type: {type(data)}, expected dict")
        return schema["defaults"].copy(), list(schema["required"]), [f"Invalid input type: {type(data)}"]
    
    normalized = {}
    missing = []
    warnings = []
    
    # Check required fields
    for field in schema["required"]:
        if field not in data or data[field] is None:
            missing.append(field)
            normalized[field] = schema["defaults"].get(field)
            warnings.append(f"Missing required field '{field}', using default: {normalized[field]}")
        else:
            normalized[field] = data[field]
    
    # Process optional fields
    for field in schema["optional"]:
        if field in data and data[field] is not None:
            normalized[field] = data[field]
        else:
            normalized[field] = schema["defaults"].get(field)
    
    # Validate and clamp numeric ranges
    for field, (min_val, max_val) in schema.get("numeric_ranges", {}).items():
        if field in normalized and normalized[field] is not None:
            try:
                val = float(normalized[field])
                if val < min_val or val > max_val:
                    old_val = val
                    val = max(min_val, min(max_val, val))
                    warnings.append(f"Field '{field}' clamped from {old_val} to {val}")
                normalized[field] = val
            except (TypeError, ValueError) as e:
                warnings.append(f"Field '{field}' has invalid value '{normalized[field]}', using default")
                normalized[field] = schema["defaults"].get(field)
    
    # Ensure type consistency
    for field in ["src_port", "dst_port", "open_ports", "process_count", 
                  "suspicious_processes", "packet_count"]:
        if field in normalized:
            try:
                normalized[field] = int(float(normalized[field]))
            except (TypeError, ValueError):
                normalized[field] = schema["defaults"].get(field, 0)
    
    for field in ["duration", "src_bytes", "dst_bytes", "total_bytes",
                  "cpu_usage", "memory_usage", "disk_usage"]:
        if field in normalized:
            try:
                normalized[field] = float(normalized[field])
            except (TypeError, ValueError):
                normalized[field] = schema["defaults"].get(field, 0.0)
    
    if missing:
        logger.warning(f"[{model_name}] Missing required fields: {missing}")
    if warnings:
        for w in warnings:
            logger.debug(f"[{model_name}] {w}")
    
    return normalized, missing, warnings


def has_web_content(data: Dict[str, Any]) -> bool:
    """Check if web data has at least one content field."""
    return bool(
        data.get("payload") or 
        data.get("response") or 
        data.get("url")
    )


# =============================================================================
# CONFIDENCE CALIBRATION UTILITIES
# =============================================================================

def min_max_normalize(value: float, min_val: float = 0.0, max_val: float = 1.0) -> float:
    """Normalize value to 0-100 scale."""
    if max_val == min_val:
        return 50.0
    normalized = (value - min_val) / (max_val - min_val)
    return max(0.0, min(100.0, normalized * 100.0))


def calculate_calibrated_risk(
    network_pred: Optional[Any],
    system_pred: Optional[Any],
    web_pred: Optional[Any]
) -> Tuple[float, str, bool, List[str]]:
    """
    Calculate calibrated global risk score using min-max normalization.
    
    Returns:
        Tuple of (risk_score, status, degraded_mode, model_statuses)
    """
    scores = []
    model_statuses = []
    degraded_mode = False
    
    # Network risk calibration (probability 0-1 -> 0-100)
    if network_pred:
        net_score = min_max_normalize(network_pred.attack_probability, 0.0, 1.0)
        # Boost for critical/high severity
        if network_pred.risk_level == "CRITICAL":
            net_score = max(net_score, 95.0)
        elif network_pred.risk_level == "HIGH":
            net_score = max(net_score, 75.0)
        scores.append(("network", net_score, 0.4))
        model_statuses.append("network: OK")
    else:
        degraded_mode = True
        model_statuses.append("network: FAILED")
    
    # System risk calibration (risk_score is already 0-100)
    if system_pred:
        sys_score = system_pred.risk_score  # Already 0-100
        if system_pred.risk_level == "compromised":
            sys_score = max(sys_score, 90.0)
        elif system_pred.risk_level == "at-risk":
            sys_score = max(sys_score, 60.0)
        scores.append(("system", sys_score, 0.35))
        model_statuses.append("system: OK")
    else:
        degraded_mode = True
        model_statuses.append("system: FAILED")
    
    # Web risk calibration (confidence 0-1 -> 0-100, but only if vulnerable)
    if web_pred:
        if web_pred.is_vulnerable:
            web_score = min_max_normalize(web_pred.confidence, 0.0, 1.0)
        else:
            web_score = 0.0
        
        if web_pred.severity == "CRITICAL":
            web_score = max(web_score, 95.0)
        elif web_pred.severity == "HIGH":
            web_score = max(web_score, 70.0)
        scores.append(("web", web_score, 0.25))
        model_statuses.append("web: OK")
    else:
        degraded_mode = True
        model_statuses.append("web: FAILED")
    
    # Calculate weighted overall risk
    if scores:
        total_weight = sum(w for _, _, w in scores)
        weighted_sum = sum(score * weight for _, score, weight in scores)
        overall_risk = weighted_sum / total_weight if total_weight > 0 else 0.0
    else:
        overall_risk = 0.0
        degraded_mode = True
    
    # Determine global status
    if overall_risk >= 85:
        global_status = "CRITICAL"
    elif overall_risk >= 70:
        global_status = "HIGH"
    elif overall_risk >= 40:
        global_status = "MEDIUM"
    else:
        global_status = "LOW"
    
    # Boost if any single model detects critical
    critical_detected = False
    if network_pred and network_pred.risk_level == "CRITICAL":
        critical_detected = True
    if system_pred and system_pred.risk_level == "compromised":
        critical_detected = True
    if web_pred and web_pred.severity == "CRITICAL":
        critical_detected = True
    
    if critical_detected and global_status != "CRITICAL":
        global_status = "HIGH" if global_status == "MEDIUM" else "CRITICAL"
    
    return round(overall_risk, 2), global_status, degraded_mode, model_statuses

# Model paths
MODEL_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "models")

NETWORK_BINARY_MODEL = os.path.join(MODEL_DIR, "network_model_binary.pkl")
NETWORK_MULTICLASS_MODEL = os.path.join(MODEL_DIR, "network_model_multiclass.pkl")
NETWORK_PREPROCESSOR = os.path.join(MODEL_DIR, "network_preprocessor.pkl")
NETWORK_FEATURE_ENGINEER = os.path.join(MODEL_DIR, "network_feature_engineer.pkl")
NETWORK_METADATA = os.path.join(MODEL_DIR, "network_model_metadata.json")

SYSTEM_MODEL = os.path.join(MODEL_DIR, "system", "system_security_model.pkl")
SYSTEM_ENCODER = os.path.join(MODEL_DIR, "system", "system_encoder.pkl")
SYSTEM_FEATURES = os.path.join(MODEL_DIR, "system", "system_feature_names.json")

WEB_MODEL = os.path.join(MODEL_DIR, "web_model.pkl")
WEB_VECTORIZER = os.path.join(MODEL_DIR, "web_vectorizer.pkl")


@dataclass
class NetworkPrediction:
    """Network intrusion detection prediction result."""
    is_attack: bool
    attack_probability: float
    attack_category: str
    attack_confidence: float
    all_probabilities: Dict[str, float]
    risk_level: str  # LOW, MEDIUM, HIGH, CRITICAL
    model_status: str = "ok"  # ok, degraded, failed
    missing_inputs: List[str] = field(default_factory=list)


@dataclass
class SystemPrediction:
    """System security analysis prediction result."""
    risk_level: str  # secure, at-risk, compromised
    risk_score: float
    anomaly_score: float
    details: Dict[str, Any]
    model_status: str = "ok"
    missing_inputs: List[str] = field(default_factory=list)


@dataclass
class WebPrediction:
    """Web vulnerability prediction result."""
    is_vulnerable: bool
    vulnerability_type: str
    confidence: float
    severity: str  # LOW, MEDIUM, HIGH, CRITICAL
    top_indicators: List[str]
    model_status: str = "ok"
    missing_inputs: List[str] = field(default_factory=list)


@dataclass
class UnifiedPrediction:
    """Combined prediction from all models."""
    network: Optional[NetworkPrediction]
    system: Optional[SystemPrediction]
    web: Optional[WebPrediction]
    global_risk_score: float  # 0-100
    global_status: str  # LOW, MEDIUM, HIGH, CRITICAL
    degraded_mode: bool
    missing_inputs: Dict[str, List[str]]
    model_statuses: List[str]
    timestamp: str
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "network": asdict(self.network) if self.network else None,
            "system": asdict(self.system) if self.system else None,
            "web": asdict(self.web) if self.web else None,
            "global_risk_score": self.global_risk_score,
            "global_status": self.global_status,
            "degraded_mode": self.degraded_mode,
            "missing_inputs": self.missing_inputs,
            "model_statuses": self.model_statuses,
            "timestamp": self.timestamp
        }


class UnifiedSecurityMLService:
    """
    Unified AI inference service for network, system, and web security models.
    
    Singleton pattern - models loaded once at startup.
    Thread-safe for concurrent predictions.
    """
    
    _instance = None
    _lock = Lock()
    _models_loaded = False
    
    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        if not self._models_loaded:
            self._load_all_models()
    
    def _load_all_models(self):
        """Load all models at startup. Called once."""
        with self._lock:
            if self._models_loaded:
                return
            
            logger.info("=" * 60)
            logger.info("LOADING UNIFIED SECURITY ML MODELS")
            logger.info("=" * 60)
            
            # Network models
            self._network_binary = None
            self._network_multiclass = None
            self._network_preprocessor = None
            self._network_feature_engineer = None
            self._network_metadata = None
            self._network_classes = None
            
            # System models
            self._system_model = None
            self._system_encoder = None
            self._system_features = None
            
            # Web models
            self._web_model = None
            self._web_vectorizer = None
            
            try:
                self._load_network_models()
                self._load_system_models()
                self._load_web_models()
                self._models_loaded = True
                logger.info("=" * 60)
                logger.info("✅ ALL MODELS LOADED SUCCESSFULLY")
                logger.info("=" * 60)
            except Exception as e:
                logger.error(f"❌ Error loading models: {e}")
                raise
    
    def _load_network_models(self):
        """Load network intrusion detection models."""
        logger.info("\n[1/3] Loading Network Models...")
        
        try:
            if os.path.exists(NETWORK_BINARY_MODEL):
                self._network_binary = joblib.load(NETWORK_BINARY_MODEL)
                logger.info(f"  ✓ Binary model: {os.path.basename(NETWORK_BINARY_MODEL)}")
            else:
                logger.warning(f"  ⚠ Binary model not found: {NETWORK_BINARY_MODEL}")
            
            if os.path.exists(NETWORK_MULTICLASS_MODEL):
                self._network_multiclass = joblib.load(NETWORK_MULTICLASS_MODEL)
                logger.info(f"  ✓ Multiclass model: {os.path.basename(NETWORK_MULTICLASS_MODEL)}")
            else:
                logger.warning(f"  ⚠ Multiclass model not found: {NETWORK_MULTICLASS_MODEL}")
            
            if os.path.exists(NETWORK_PREPROCESSOR):
                self._network_preprocessor = joblib.load(NETWORK_PREPROCESSOR)
                logger.info(f"  ✓ Preprocessor: {os.path.basename(NETWORK_PREPROCESSOR)}")
            
            if os.path.exists(NETWORK_FEATURE_ENGINEER):
                self._network_feature_engineer = joblib.load(NETWORK_FEATURE_ENGINEER)
                logger.info(f"  ✓ Feature engineer: {os.path.basename(NETWORK_FEATURE_ENGINEER)}")
            
            if os.path.exists(NETWORK_METADATA):
                with open(NETWORK_METADATA, 'r') as f:
                    self._network_metadata = json.load(f)
                    self._network_classes = self._network_metadata.get('class_names', 
                        ['Normal', 'DoS', 'Probe', 'R2L', 'U2R', 'Other'])
                logger.info(f"  ✓ Metadata: {os.path.basename(NETWORK_METADATA)}")
            else:
                self._network_classes = ['Normal', 'DoS', 'Probe', 'R2L', 'U2R', 'Other']
            
            logger.info(f"  ✓ Attack categories: {', '.join(self._network_classes)}")
            
        except Exception as e:
            logger.error(f"  ❌ Failed to load network models: {e}")
    
    def _load_system_models(self):
        """Load system security models."""
        logger.info("\n[2/3] Loading System Models...")
        
        try:
            if os.path.exists(SYSTEM_MODEL):
                self._system_model = joblib.load(SYSTEM_MODEL)
                logger.info(f"  ✓ System model: {os.path.basename(SYSTEM_MODEL)}")
            else:
                logger.warning(f"  ⚠ System model not found: {SYSTEM_MODEL}")
            
            if os.path.exists(SYSTEM_ENCODER):
                self._system_encoder = joblib.load(SYSTEM_ENCODER)
                logger.info(f"  ✓ System encoder: {os.path.basename(SYSTEM_ENCODER)}")
            
            if os.path.exists(SYSTEM_FEATURES):
                with open(SYSTEM_FEATURES, 'r') as f:
                    self._system_features = json.load(f)
                logger.info(f"  ✓ System features: {os.path.basename(SYSTEM_FEATURES)}")
            
        except Exception as e:
            logger.error(f"  ❌ Failed to load system models: {e}")
    
    def _load_web_models(self):
        """Load web vulnerability models."""
        logger.info("\n[3/3] Loading Web Models...")
        
        try:
            if os.path.exists(WEB_MODEL):
                self._web_model = joblib.load(WEB_MODEL)
                logger.info(f"  ✓ Web model: {os.path.basename(WEB_MODEL)}")
            else:
                logger.warning(f"  ⚠ Web model not found: {WEB_MODEL}")
            
            if os.path.exists(WEB_VECTORIZER):
                self._web_vectorizer = joblib.load(WEB_VECTORIZER)
                logger.info(f"  ✓ Web vectorizer: {os.path.basename(WEB_VECTORIZER)}")
            
        except Exception as e:
            logger.error(f"  ❌ Failed to load web models: {e}")
    
    def predict_network(self, network_data: Dict[str, Any]) -> Optional[NetworkPrediction]:
        """
        Predict network intrusion with input validation.
        
        Args:
            network_data: Dictionary with network flow features
            
        Returns:
            NetworkPrediction with binary and multiclass results
        """
        if not self._network_binary:
            logger.warning("[network] Binary model not loaded, returning None")
            return None
        
        # Validate and normalize input
        normalized_data, missing, warnings = validate_and_normalize_input(
            network_data, NETWORK_SCHEMA, "network"
        )
        
        model_status = "ok" if not missing else "degraded"
        
        try:
            # Build engineered feature vector (56 features)
            X = self._build_network_features(normalized_data)
            
            # Binary prediction
            binary_proba = self._network_binary.predict_proba(X)[0]
            is_attack = bool(binary_proba[1] > 0.5)
            attack_prob = float(binary_proba[1])
            
            # Multiclass prediction
            if self._network_multiclass:
                multiclass_proba = self._network_multiclass.predict_proba(X)[0]
                pred_class = int(np.argmax(multiclass_proba))
                attack_category = self._network_classes[pred_class] if pred_class < len(self._network_classes) else "Unknown"
                attack_confidence = float(multiclass_proba[pred_class])
                all_probs = {cls: float(prob) for cls, prob in zip(self._network_classes, multiclass_proba)}
            else:
                attack_category = "Attack" if is_attack else "Normal"
                attack_confidence = attack_prob
                all_probs = {"Normal": float(binary_proba[0]), "Attack": float(binary_proba[1])}
            
            # Risk level
            if attack_prob < 0.3:
                risk_level = "LOW"
            elif attack_prob < 0.6:
                risk_level = "MEDIUM"
            elif attack_prob < 0.85:
                risk_level = "HIGH"
            else:
                risk_level = "CRITICAL"
            
            logger.info(f"[network] Prediction: {attack_category}, risk={risk_level}, prob={attack_prob:.3f}")
            
            return NetworkPrediction(
                is_attack=is_attack,
                attack_probability=attack_prob,
                attack_category=attack_category,
                attack_confidence=attack_confidence,
                all_probabilities=all_probs,
                risk_level=risk_level,
                model_status=model_status,
                missing_inputs=missing
            )
            
        except Exception as e:
            logger.error(f"[network] Prediction failed: {e}")
            import traceback
            logger.debug(traceback.format_exc())
            # Return degraded prediction
            return NetworkPrediction(
                is_attack=False,
                attack_probability=0.0,
                attack_category="Unknown",
                attack_confidence=0.0,
                all_probabilities={},
                risk_level="UNKNOWN",
                model_status="failed",
                missing_inputs=missing
            )
    
    def _build_network_features(self, network_data: Dict[str, Any]) -> np.ndarray:
        """Build 56 engineered features from raw network data."""
        # Extract raw features with defaults
        duration = float(network_data.get('duration', 0))
        src_bytes = float(network_data.get('src_bytes', 0))
        dst_bytes = float(network_data.get('dst_bytes', 0))
        total_bytes = float(network_data.get('total_bytes', src_bytes + dst_bytes))
        packet_count = float(network_data.get('packet_count', 0))
        src_packets = float(network_data.get('src_packets', packet_count / 2))
        dst_packets = float(network_data.get('dst_packets', packet_count / 2))
        
        # Protocol
        protocol = str(network_data.get('protocol', 'tcp')).lower()
        protocol_tcp = 1 if protocol == 'tcp' else 0
        protocol_udp = 1 if protocol == 'udp' else 0
        protocol_icmp = 1 if protocol == 'icmp' else 0
        
        # Service from port
        dst_port = int(network_data.get('dst_port', 80))
        service_map = {
            80: 'http', 443: 'https', 8080: 'http',
            22: 'ssh', 21: 'ftp', 23: 'telnet',
            25: 'smtp', 53: 'dns', 110: 'pop3'
        }
        service = service_map.get(dst_port, 'other')
        service_http = 1 if service == 'http' else 0
        service_https = 1 if service == 'https' else 0
        service_ssh = 1 if service == 'ssh' else 0
        service_ftp = 1 if service == 'ftp' else 0
        service_dns = 1 if service == 'dns' else 0
        service_smtp = 1 if service == 'smtp' else 0
        service_other = 1 if service not in ['http', 'https', 'ssh', 'ftp', 'dns', 'smtp'] else 0
        
        # Flags
        syn_flag = int(network_data.get('syn_flag', 0))
        ack_flag = int(network_data.get('ack_flag', 0))
        rst_flag = int(network_data.get('rst_flag', 0))
        fin_flag = int(network_data.get('fin_flag', 0))
        
        # Derived features
        bytes_per_second = src_bytes / duration if duration > 0 else 0
        packets_per_second = packet_count / duration if duration > 0 else 0
        avg_packet_size = total_bytes / packet_count if packet_count > 0 else 0
        
        # Time-based (simplified - single flow context)
        inter_arrival_mean = duration / packet_count if packet_count > 0 else 0
        inter_arrival_std = inter_arrival_mean * 0.1  # Estimate
        
        # Connection stats (single flow)
        connection_count = 1
        unique_dst_ips = 1
        unique_dst_ports = 1
        same_src_ip_rate = 1.0
        same_dst_ip_rate = 1.0
        failed_connections = 1 if rst_flag else 0
        successful_connections = 1 if ack_flag else 0
        connection_success_rate = 1.0 if ack_flag else 0.0
        
        # Flag counts
        syn_flag_count = syn_flag
        ack_flag_count = ack_flag
        rst_flag_count = rst_flag
        fin_flag_count = fin_flag
        
        # Ratios
        syn_to_ack_ratio = syn_flag / ack_flag if ack_flag > 0 else 0
        rst_to_total_ratio = rst_flag / packet_count if packet_count > 0 else 0
        
        # Time window features (simplified)
        connections_last_1s = 1 if duration <= 1 else 0
        connections_last_10s = 1 if duration <= 10 else 0
        connections_last_60s = 1 if duration <= 60 else 0
        bytes_last_10s = total_bytes if duration <= 10 else total_bytes * 10 / max(duration, 10)
        packets_last_10s = packet_count if duration <= 10 else packet_count * 10 / max(duration, 10)
        
        # Rates
        request_rate = packets_per_second
        burst_rate = packets_per_second * 2  # Simplified
        time_since_last = duration
        
        # Flag encoding
        flag_sf = 1 if syn_flag and fin_flag else 0
        flag_rej = 1 if rst_flag else 0
        flag_s0 = 1 if syn_flag and not ack_flag else 0
        flag_other = 1 if not (flag_sf or flag_rej or flag_s0) else 0
        
        # Port categorization
        is_well_known = 1 if dst_port < 1024 else 0
        is_registered = 1 if 1024 <= dst_port < 49152 else 0
        is_dynamic = 1 if dst_port >= 49152 else 0
        port_entropy = 0.5  # Simplified for single flow
        
        # Build feature vector in correct order
        features = [
            duration, src_bytes, dst_bytes, total_bytes,
            packet_count, src_packets, dst_packets,
            bytes_per_second, packets_per_second,
            avg_packet_size,
            avg_packet_size, inter_arrival_std,  # packet_size_mean=avg, std=estimate
            avg_packet_size * 0.8, avg_packet_size * 1.2,  # min/max estimates
            inter_arrival_mean, inter_arrival_std,
            connection_count, unique_dst_ips, unique_dst_ports,
            same_src_ip_rate, same_dst_ip_rate,
            failed_connections, successful_connections, connection_success_rate,
            syn_flag_count, ack_flag_count, rst_flag_count, fin_flag_count,
            syn_to_ack_ratio, rst_to_total_ratio,
            connections_last_1s, connections_last_10s, connections_last_60s,
            bytes_last_10s, packets_last_10s,
            request_rate, burst_rate, time_since_last,
            protocol_tcp, protocol_udp, protocol_icmp,
            service_http, service_https, service_ssh, service_ftp, service_dns, service_smtp, service_other,
            flag_sf, flag_rej, flag_s0, flag_other,
            is_well_known, is_registered, is_dynamic, port_entropy
        ]
        
        # Ensure 56 features
        while len(features) < 56:
            features.append(0.0)
        features = features[:56]
        
        return np.array(features).reshape(1, -1)
    
    def predict_system(self, system_data: Dict[str, Any]) -> Optional[SystemPrediction]:
        """
        Predict system security risk with input validation.
        
        Args:
            system_data: Dictionary with system metrics
            
        Returns:
            SystemPrediction with risk level and score
        """
        if not self._system_model:
            logger.warning("[system] Model not loaded, returning None")
            return None
        
        # Validate and normalize input
        normalized_data, missing, warnings = validate_and_normalize_input(
            system_data, SYSTEM_SCHEMA, "system"
        )
        
        model_status = "ok" if not missing else "degraded"
        
        try:
            # Prepare features - system_features is a list of feature names
            if self._system_features and isinstance(self._system_features, list):
                feature_names = self._system_features
                features = [normalized_data.get(f, 0) for f in feature_names]
            elif self._system_features and isinstance(self._system_features, dict):
                feature_names = self._system_features.get('features', [])
                features = [normalized_data.get(f, 0) for f in feature_names]
            else:
                features = list(normalized_data.values())
            
            X = np.array(features).reshape(1, -1)
            
            # Handle categorical encoding if encoder exists
            if self._system_encoder and hasattr(self._system_encoder, 'transform'):
                try:
                    X = self._system_encoder.transform(X)
                except Exception as e:
                    logger.debug(f"[system] Encoder transform failed: {e}")
            
            # Prediction
            if hasattr(self._system_model, 'predict_proba'):
                proba = self._system_model.predict_proba(X)[0]
                pred_class = int(np.argmax(proba))
                confidence = float(np.max(proba))
            else:
                pred_class = int(self._system_model.predict(X)[0])
                confidence = 0.8
            
            # Map to risk levels
            risk_mapping = {0: "secure", 1: "at-risk", 2: "compromised"}
            risk_level = risk_mapping.get(pred_class, "unknown")
            risk_score = float(confidence * 100)
            
            # Anomaly score (inverted confidence for secure predictions)
            if risk_level == "secure":
                anomaly_score = 1.0 - confidence
            else:
                anomaly_score = confidence
            
            logger.info(f"[system] Prediction: {risk_level}, score={risk_score:.1f}, confidence={confidence:.3f}")
            
            return SystemPrediction(
                risk_level=risk_level,
                risk_score=risk_score,
                anomaly_score=float(anomaly_score),
                details={
                    "predicted_class": pred_class,
                    "confidence": confidence,
                    "raw_features": features[:10]  # First 10 features only
                },
                model_status=model_status,
                missing_inputs=missing
            )
            
        except Exception as e:
            logger.error(f"[system] Prediction failed: {e}")
            import traceback
            logger.debug(traceback.format_exc())
            # Return degraded prediction
            return SystemPrediction(
                risk_level="unknown",
                risk_score=0.0,
                anomaly_score=0.0,
                details={"error": str(e)},
                model_status="failed",
                missing_inputs=missing
            )
    
    def predict_web(self, web_data: Dict[str, Any]) -> Optional[WebPrediction]:
        """
        Predict web vulnerability with input validation.
        
        Args:
            web_data: Dictionary with web payload/response data
            
        Returns:
            WebPrediction with vulnerability classification
        """
        if not self._web_model or not self._web_vectorizer:
            logger.warning("[web] Models not loaded, returning None")
            return None
        
        # Validate and normalize input
        normalized_data, missing, warnings = validate_and_normalize_input(
            web_data, WEB_SCHEMA, "web"
        )
        
        # Check for content
        if not has_web_content(normalized_data):
            missing.append("content (payload/response/url)")
            logger.warning("[web] No content provided (payload/response/url)")
        
        model_status = "ok" if not missing else "degraded"
        
        try:
            # Extract text data for vectorization
            text = (normalized_data.get('payload', '') or 
                   normalized_data.get('response', '') or 
                   normalized_data.get('url', ''))
            if not text:
                text = str(normalized_data)
            
            # Vectorize
            X = self._web_vectorizer.transform([text])
            
            # Prediction
            if hasattr(self._web_model, 'predict_proba'):
                proba = self._web_model.predict_proba(X)[0]
                pred_class = int(np.argmax(proba))
                confidence = float(np.max(proba))
            else:
                pred_class = int(self._web_model.predict(X)[0])
                confidence = 0.8
            
            # Map predictions
            vuln_types = {0: "None", 1: "SQL Injection", 2: "XSS", 3: "Path Traversal", 
                         4: "Command Injection", 5: "Other"}
            vuln_type = vuln_types.get(pred_class, "Unknown")
            is_vulnerable = pred_class != 0
            
            # Severity mapping
            if pred_class == 0:
                severity = "NONE"
            elif confidence > 0.9:
                severity = "CRITICAL"
            elif confidence > 0.7:
                severity = "HIGH"
            elif confidence > 0.5:
                severity = "MEDIUM"
            else:
                severity = "LOW"
            
            # Extract indicators from text
            indicators = []
            suspicious_patterns = [
                ('script', 'JavaScript/XSS'),
                ('select', 'SQL keywords'),
                ('union', 'SQL injection'),
                ('../', 'Path traversal'),
                ('exec', 'Command injection'),
                ('eval', 'Code execution'),
                ('<iframe', 'Iframe injection'),
                ('javascript:', 'JS protocol')
            ]
            text_lower = text.lower()
            for pattern, desc in suspicious_patterns:
                if pattern in text_lower:
                    indicators.append(desc)
            
            logger.info(f"[web] Prediction: {vuln_type}, severity={severity}, confidence={confidence:.3f}")
            
            return WebPrediction(
                is_vulnerable=is_vulnerable,
                vulnerability_type=vuln_type,
                confidence=confidence,
                severity=severity,
                top_indicators=indicators[:5],
                model_status=model_status,
                missing_inputs=missing
            )
            
        except Exception as e:
            logger.error(f"[web] Prediction failed: {e}")
            import traceback
            logger.debug(traceback.format_exc())
            # Return degraded prediction
            return WebPrediction(
                is_vulnerable=False,
                vulnerability_type="Unknown",
                confidence=0.0,
                severity="UNKNOWN",
                top_indicators=[],
                model_status="failed",
                missing_inputs=missing
            )
    
    def predict_all(self, input_bundle: Dict[str, Any]) -> UnifiedPrediction:
        """
        Run all predictions and compute calibrated global risk.
        
        Args:
            input_bundle: Dictionary with keys 'network', 'system', 'web'
            
        Returns:
            UnifiedPrediction with all results and global risk assessment
        """
        logger.info("[unified] Running unified security prediction...")
        
        network_input = input_bundle.get('network')
        system_input = input_bundle.get('system')
        web_input = input_bundle.get('web')
        
        # Track missing inputs across all models
        all_missing: Dict[str, List[str]] = {}
        
        # Run predictions with safe failure handling
        try:
            network_pred = self.predict_network(network_input) if network_input else None
            if network_pred:
                all_missing['network'] = network_pred.missing_inputs
        except Exception as e:
            logger.error(f"[unified] Network prediction failed: {e}")
            network_pred = None
            all_missing['network'] = ['prediction_failed']
        
        try:
            system_pred = self.predict_system(system_input) if system_input else None
            if system_pred:
                all_missing['system'] = system_pred.missing_inputs
        except Exception as e:
            logger.error(f"[unified] System prediction failed: {e}")
            system_pred = None
            all_missing['system'] = ['prediction_failed']
        
        try:
            web_pred = self.predict_web(web_input) if web_input else None
            if web_pred:
                all_missing['web'] = web_pred.missing_inputs
        except Exception as e:
            logger.error(f"[unified] Web prediction failed: {e}")
            web_pred = None
            all_missing['web'] = ['prediction_failed']
        
        # Calculate calibrated global risk
        overall_risk, global_status, degraded_mode, model_statuses = calculate_calibrated_risk(
            network_pred, system_pred, web_pred
        )
        
        logger.info(f"[unified] Global risk: {overall_risk}, Status: {global_status}, Degraded: {degraded_mode}")
        
        return UnifiedPrediction(
            network=network_pred,
            system=system_pred,
            web=web_pred,
            global_risk_score=overall_risk,
            global_status=global_status,
            degraded_mode=degraded_mode,
            missing_inputs=all_missing,
            model_statuses=model_statuses,
            timestamp=datetime.now(timezone.utc).isoformat()
        )
    
    def get_model_status(self) -> Dict[str, Any]:
        """Get status of all loaded models."""
        return {
            "network": {
                "binary_loaded": self._network_binary is not None,
                "multiclass_loaded": self._network_multiclass is not None,
                "preprocessor_loaded": self._network_preprocessor is not None,
                "feature_engineer_loaded": self._network_feature_engineer is not None,
                "attack_categories": self._network_classes
            },
            "system": {
                "model_loaded": self._system_model is not None,
                "encoder_loaded": self._system_encoder is not None,
                "features_loaded": self._system_features is not None
            },
            "web": {
                "model_loaded": self._web_model is not None,
                "vectorizer_loaded": self._web_vectorizer is not None
            },
            "all_models_loaded": self._models_loaded,
            "timestamp": datetime.utcnow().isoformat()
        }
    
    def reload_models(self):
        """Reload all models (useful for hot-swapping)."""
        with self._lock:
            self._models_loaded = False
            self._load_all_models()


# Global singleton instance
_service: Optional[UnifiedSecurityMLService] = None


def get_service() -> UnifiedSecurityMLService:
    """Get the unified ML service singleton."""
    global _service
    if _service is None:
        _service = UnifiedSecurityMLService()
    return _service


def predict_network(network_data: Dict[str, Any]) -> Optional[NetworkPrediction]:
    """Convenience function for network prediction."""
    return get_service().predict_network(network_data)


def predict_system(system_data: Dict[str, Any]) -> Optional[SystemPrediction]:
    """Convenience function for system prediction."""
    return get_service().predict_system(system_data)


def predict_web(web_data: Dict[str, Any]) -> Optional[WebPrediction]:
    """Convenience function for web prediction."""
    return get_service().predict_web(web_data)


def predict_all(input_bundle: Dict[str, Any]) -> UnifiedPrediction:
    """Convenience function for unified prediction."""
    return get_service().predict_all(input_bundle)


def get_status() -> Dict[str, Any]:
    """Get model status."""
    return get_service().get_model_status()


# For testing
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
    
    service = get_service()
    
    print("\n" + "=" * 60)
    print("MODEL STATUS")
    print("=" * 60)
    status = service.get_model_status()
    print(json.dumps(status, indent=2))
    
    # Test predictions
    print("\n" + "=" * 60)
    print("TEST PREDICTIONS")
    print("=" * 60)
    
    # Network test
    network_input = {
        "duration": 1.5,
        "src_bytes": 1024,
        "dst_bytes": 2048,
        "total_bytes": 3072,
        "packet_count": 10,
        "src_packets": 5,
        "dst_packets": 5,
        "protocol": "tcp",
        "src_port": 54321,
        "dst_port": 80,
        "syn_flag": 1,
        "ack_flag": 1
    }
    
    net_pred = service.predict_network(network_input)
    if net_pred:
        print(f"\n🌐 Network: {net_pred.attack_category} (prob: {net_pred.attack_probability:.2f})")
    
    # System test
    system_input = {
        "cpu_usage": 45.5,
        "memory_usage": 60.2,
        "disk_usage": 55.0,
        "process_count": 150,
        "open_ports": 12
    }
    
    sys_pred = service.predict_system(system_input)
    if sys_pred:
        print(f"🔧 System: {sys_pred.risk_level} (score: {sys_pred.risk_score:.1f})")
    
    # Web test
    web_input = {
        "url": "/api/search?q=test",
        "payload": "<script>alert('xss')</script>",
        "method": "POST"
    }
    
    web_pred = service.predict_web(web_input)
    if web_pred:
        print(f"🌐 Web: {web_pred.vulnerability_type} (severity: {web_pred.severity})")
    
    # Unified test
    print("\n" + "=" * 60)
    print("UNIFIED PREDICTION")
    print("=" * 60)
    
    unified = service.predict_all({
        "network": network_input,
        "system": system_input,
        "web": web_input
    })
    
    print(f"Global Risk Score: {unified.global_risk_score}")
    print(f"Global Status: {unified.global_status}")
    print(f"Degraded Mode: {unified.degraded_mode}")
    print(f"Missing Inputs: {unified.missing_inputs}")
    print(f"Model Statuses: {unified.model_statuses}")
    print(f"Timestamp: {unified.timestamp}")
    
    print("\n" + "=" * 60)
    print("STRUCTURED OUTPUT (to_dict)")
    print("=" * 60)
    import json
    print(json.dumps(unified.to_dict(), indent=2, default=str))
