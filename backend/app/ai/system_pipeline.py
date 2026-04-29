"""
System AI Pipeline - Local RandomForest model inference
Analyzes system scan results using trained security model
"""
import logging
import pandas as pd
from .loader import get_system_model

logger = logging.getLogger(__name__)


def extract_system_features(scan_result):
    """
    Extract numerical features from system scan output.
    Must match features used during training.
    """
    features = {}
    
    # Get system_data if available (from system scanner)
    system_data = scan_result.get("system_data", {})
    
    # Use system_data if available, otherwise fall back to scan_result directly
    data_source = system_data if system_data else scan_result
    
    # User features
    users = data_source.get("users", [])
    features["user_count"] = len(users)
    features["admin_count"] = sum(1 for u in users if isinstance(u, dict) and u.get("is_admin", False))
    suspicious_user_names = ["admin", "root", "test", "guest", "user", "support"]
    features["suspicious_users"] = sum(1 for u in users if isinstance(u, dict) and 
                                       any(s in str(u.get("name", "")).lower() for s in suspicious_user_names))
    
    # Service features
    services = data_source.get("services", [])
    features["service_count"] = len(services)
    insecure_svcs = ["telnet", "ftp", "rsh", "rlogin", "nfs", "smb"]
    features["insecure_services"] = sum(1 for s in services if isinstance(s, str) and 
                                         any(i in s.lower() for i in insecure_svcs))
    exposed_ports = [21, 23, 25, 53, 80, 110, 143, 445, 3306, 5432, 8080, 8443]
    features["exposed_services"] = sum(1 for s in services if isinstance(s, dict) and 
                                       s.get("port") in exposed_ports)
    
    # Package features
    packages = data_source.get("packages", [])
    features["package_count"] = len(packages)
    features["outdated_packages"] = sum(1 for p in packages if isinstance(p, dict) and p.get("outdated", False))
    
    # Process features
    processes = data_source.get("processes", [])
    features["process_count"] = len(processes)
    suspicious_procs = ["nc", "netcat", "nmap", "meterpreter", "backdoor", "trojan"]
    features["suspicious_processes"] = sum(1 for p in processes if isinstance(p, dict) and 
                                           any(s in str(p.get("name", "")).lower() for s in suspicious_procs))
    
    # Vulnerability features
    vulns = scan_result.get("vulnerabilities", scan_result.get("findings", []))
    features["total_vulns"] = len(vulns)
    features["critical_vulns"] = sum(1 for v in vulns if isinstance(v, dict) and str(v.get("severity", "")).upper() == "CRITICAL")
    features["high_vulns"] = sum(1 for v in vulns if isinstance(v, dict) and str(v.get("severity", "")).upper() == "HIGH")
    features["medium_vulns"] = sum(1 for v in vulns if isinstance(v, dict) and str(v.get("severity", "")).upper() == "MEDIUM")
    features["low_vulns"] = sum(1 for v in vulns if isinstance(v, dict) and str(v.get("severity", "")).upper() == "LOW")
    
    # Network features
    network = data_source.get("network", {})
    features["open_ports"] = len(network.get("open_ports", []))
    firewall = data_source.get("firewall", {})
    features["firewall_enabled"] = 1 if firewall.get("enabled", False) else 0
    
    # OS features
    os_info = data_source.get("os_info", {})
    features["is_linux"] = 1 if "linux" in str(os_info.get("name", "")).lower() else 0
    features["is_windows"] = 1 if "windows" in str(os_info.get("name", "")).lower() else 0
    
    return features


def analyze_system(scan_result):
    """
    Run AI analysis on system scan results.
    Uses local RandomForest model for security classification.
    Returns: secure (1) or at-risk (0)
    """
    model = get_system_model()
    if model is None:
        return {
            "error": "System security model not available",
            "prediction": "unknown",
            "confidence": 0.0
        }

    try:
        # Extract features from scan result
        features = extract_system_features(scan_result)
        
        # Convert to DataFrame with correct column order
        feature_df = pd.DataFrame([features])
        
        # Ensure columns match model expectation
        if hasattr(model, "feature_names_in_"):
            expected_features = list(model.feature_names_in_)
            # Reorder columns to match training
            feature_df = feature_df[expected_features]
        
        # Run prediction
        prediction = model.predict(feature_df)[0]
        
        # Get probability if available
        if hasattr(model, "predict_proba"):
            probabilities = model.predict_proba(feature_df)[0]
            confidence = float(max(probabilities))
        else:
            confidence = 1.0
        
        # Map prediction: 1 = secure/normal, 0 = at-risk/vulnerable
        prediction_label = "secure" if prediction == 1 else "at-risk"
        
        return {
            "prediction": prediction_label,
            "confidence": round(confidence, 3),
            "features_used": features,
            "model_type": "RandomForest"
        }

    except Exception as e:
        logger.error(f"System AI analysis failed: {str(e)}")
        return {
            "error": str(e),
            "prediction": "error",
            "confidence": 0.0
        }
