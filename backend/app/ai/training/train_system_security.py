"""
Train System Security Model
Features extracted from system scanner output:
- user_count, admin_count, suspicious_users
- service_count, exposed_services, insecure_services
- package_count, outdated_packages
- process_count, suspicious_processes
- vulnerability_counts by severity
- network_ports_open, firewall_enabled
"""
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report
import joblib
import os


def extract_features_from_scan(scan_data):
    """Extract numerical features from system scan output"""
    features = {}
    
    # User features
    users = scan_data.get("users", [])
    features["user_count"] = len(users)
    features["admin_count"] = sum(1 for u in users if isinstance(u, dict) and u.get("is_admin", False))
    suspicious_user_names = ["admin", "root", "test", "guest", "user", "support"]
    features["suspicious_users"] = sum(1 for u in users if isinstance(u, dict) and 
                                       any(s in str(u.get("name", "")).lower() for s in suspicious_user_names))
    
    # Service features
    services = scan_data.get("services", [])
    features["service_count"] = len(services)
    insecure_svcs = ["telnet", "ftp", "rsh", "rlogin", "nfs", "smb"]
    features["insecure_services"] = sum(1 for s in services if isinstance(s, str) and 
                                         any(i in s.lower() for i in insecure_svcs))
    exposed_ports = [21, 23, 25, 53, 80, 110, 143, 445, 3306, 5432, 8080, 8443]
    features["exposed_services"] = sum(1 for s in services if isinstance(s, dict) and 
                                       s.get("port") in exposed_ports)
    
    # Package features
    packages = scan_data.get("packages", [])
    features["package_count"] = len(packages)
    features["outdated_packages"] = sum(1 for p in packages if isinstance(p, dict) and p.get("outdated", False))
    
    # Process features
    processes = scan_data.get("processes", [])
    features["process_count"] = len(processes)
    suspicious_procs = ["nc", "netcat", "nmap", "meterpreter", "backdoor", "trojan"]
    features["suspicious_processes"] = sum(1 for p in processes if isinstance(p, dict) and 
                                           any(s in str(p.get("name", "")).lower() for s in suspicious_procs))
    
    # Vulnerability features
    vulns = scan_data.get("vulnerabilities", scan_data.get("findings", []))
    features["total_vulns"] = len(vulns)
    features["critical_vulns"] = sum(1 for v in vulns if isinstance(v, dict) and str(v.get("severity", "")).upper() == "CRITICAL")
    features["high_vulns"] = sum(1 for v in vulns if isinstance(v, dict) and str(v.get("severity", "")).upper() == "HIGH")
    features["medium_vulns"] = sum(1 for v in vulns if isinstance(v, dict) and str(v.get("severity", "")).upper() == "MEDIUM")
    features["low_vulns"] = sum(1 for v in vulns if isinstance(v, dict) and str(v.get("severity", "")).upper() == "LOW")
    
    # Network features
    network = scan_data.get("network", {})
    features["open_ports"] = len(network.get("open_ports", []))
    firewall = scan_data.get("firewall", {})
    features["firewall_enabled"] = 1 if firewall.get("enabled", False) else 0
    
    # OS features
    os_info = scan_data.get("os_info", {})
    features["is_linux"] = 1 if "linux" in str(os_info.get("name", "")).lower() else 0
    features["is_windows"] = 1 if "windows" in str(os_info.get("name", "")).lower() else 0
    
    return features


def generate_synthetic_training_data(n_samples=1000):
    """Generate synthetic training data based on realistic system scan patterns"""
    np.random.seed(42)
    data = []
    
    for i in range(n_samples):
        # Generate random scan profile
        is_secure = np.random.choice([0, 1], p=[0.4, 0.6])  # 60% secure, 40% at-risk
        
        if is_secure:
            # Secure system profile
            scan = {
                "users": [{"name": f"user_{j}", "is_admin": j == 0} for j in range(np.random.randint(2, 5))],
                "services": ["sshd", "nginx", "cron"],
                "packages": [{"outdated": False} for _ in range(50)],
                "processes": [{"name": "normal_process"} for _ in range(20)],
                "vulnerabilities": [{"severity": "LOW"} for _ in range(np.random.randint(0, 3))],
                "network": {"open_ports": [22, 80, 443]},
                "firewall": {"enabled": True},
                "os_info": {"name": "Linux"}
            }
        else:
            # At-risk system profile
            scan = {
                "users": [{"name": np.random.choice(["admin", "root", "test", "user"]), "is_admin": True} 
                         for _ in range(np.random.randint(3, 8))],
                "services": ["sshd", "telnet", "ftp", "nginx"],
                "packages": [{"outdated": True} for _ in range(100)],
                "processes": [{"name": np.random.choice(["nc", "normal", "suspicious"])} for _ in range(30)],
                "vulnerabilities": [
                    {"severity": "CRITICAL"} for _ in range(np.random.randint(1, 5))
                ] + [{"severity": "HIGH"} for _ in range(np.random.randint(2, 8))],
                "network": {"open_ports": [21, 23, 25, 80, 445, 3306]},
                "firewall": {"enabled": False},
                "os_info": {"name": "Linux"}
            }
        
        features = extract_features_from_scan(scan)
        features["label"] = is_secure  # 1 = secure/normal, 0 = at-risk/vulnerable
        data.append(features)
    
    return pd.DataFrame(data)


def train_system_model():
    """Train and save system security model"""
    print("Generating training data...")
    df = generate_synthetic_training_data(1000)
    
    feature_cols = [c for c in df.columns if c != "label"]
    X = df[feature_cols]
    y = df["label"]
    
    print(f"Training with {len(df)} samples, {len(feature_cols)} features")
    print(f"Feature names: {feature_cols}")
    
    # Split data
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    # Train RandomForest
    model = RandomForestClassifier(
        n_estimators=100,
        max_depth=10,
        random_state=42,
        class_weight="balanced"
    )
    model.fit(X_train, y_train)
    
    # Evaluate
    y_pred = model.predict(X_test)
    print("\n=== Model Performance ===")
    print(classification_report(y_test, y_pred, target_names=["at-risk", "secure"]))
    
    # Save model
    model_dir = "../models/system"
    os.makedirs(model_dir, exist_ok=True)
    
    joblib.dump(model, os.path.join(model_dir, "system_security_model.pkl"))
    
    # Save feature names for inference
    import json
    with open(os.path.join(model_dir, "system_feature_names.json"), "w") as f:
        json.dump(feature_cols, f)
    
    print(f"\n✅ Model saved to {model_dir}/system_security_model.pkl")
    print(f"✅ Feature names saved to {model_dir}/system_feature_names.json")
    
    return model, feature_cols


if __name__ == "__main__":
    train_system_model()
