"""
Fast Unified Network AI Training
Optimized version with sampling for quick training
Combines CICIDS2017, UNSW-NB15, CTU-13 Botnet, and NSL-KDD datasets
"""
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report
import joblib
import os
import glob
import warnings
warnings.filterwarnings('ignore')

np.random.seed(42)

DATASET_DIR = "/home/andu/AI_Baseline_Assessment_Scanner/backend/app/ai/network and botnet  datasets"
MAX_SAMPLES_PER_DATASET = 50000  # Limit samples for speed

def safe_get_column(df, col_name, default=0):
    """Safely get column or return default series"""
    if col_name in df.columns:
        return pd.to_numeric(df[col_name], errors='coerce').fillna(0)
    return pd.Series([default] * len(df), index=df.index)


def extract_features_unified(df, dataset_type):
    """Extract unified features from any dataset"""
    features = pd.DataFrame(index=df.index)
    
    if dataset_type == 'cicids':
        # CICIDS2017 mapping
        features['duration'] = safe_get_column(df, 'Flow Duration') / 1000000
        features['src_bytes'] = safe_get_column(df, 'Total Length of Fwd Packets')
        
        # For dst_bytes, try Bwd Packets or calculate from Total
        if 'Total Length of Bwd Packets' in df.columns:
            features['dst_bytes'] = safe_get_column(df, 'Total Length of Bwd Packets')
        elif 'TotLen Bwd Pkts' in df.columns:
            features['dst_bytes'] = safe_get_column(df, 'TotLen Bwd Pkts')
        else:
            features['dst_bytes'] = 0
        
        # Protocol inference from ports
        dst_port = safe_get_column(df, 'Destination Port')
        features['protocol_icmp'] = 0
        features['protocol_tcp'] = (dst_port <= 1024).astype(int)
        
        # Label
        if 'Attack Type' in df.columns:
            features['label'] = (df['Attack Type'] != 'BENIGN').astype(int)
        elif 'Label' in df.columns:
            features['label'] = (df['Label'] != 'BENIGN').astype(int)
        else:
            features['label'] = 0
            
    elif dataset_type == 'unsw':
        # UNSW-NB15 mapping
        features['duration'] = safe_get_column(df, 'Dur')
        features['src_bytes'] = safe_get_column(df, 'SrcBytes')
        tot_bytes = safe_get_column(df, 'TotBytes')
        features['dst_bytes'] = tot_bytes - features['src_bytes']
        
        # Protocol
        proto = df.get('Proto', 'tcp').str.lower()
        features['protocol_icmp'] = (proto == 'icmp').astype(int)
        features['protocol_tcp'] = ((proto == 'tcp') | (proto == 'TCP')).astype(int)
        
        # Label (last column)
        label_col = df.columns[-1]
        features['label'] = (df[label_col] != 'normal').astype(int)
        
    elif dataset_type == 'ctu':
        # CTU-13 botnet dataset
        features['duration'] = safe_get_column(df, 'Dur')
        features['src_bytes'] = safe_get_column(df, 'SrcBytes')
        tot_bytes = safe_get_column(df, 'TotBytes')
        features['dst_bytes'] = tot_bytes - features['src_bytes']
        
        # Protocol
        proto = df.get('Proto', 'tcp').str.lower()
        features['protocol_icmp'] = (proto == 'icmp').astype(int)
        features['protocol_tcp'] = ((proto == 'tcp') | (proto == 'TCP')).astype(int)
        
        # Label - Background = normal, botnet/attack = anomaly
        label_col = df.columns[-1]
        features['label'] = (~df[label_col].str.contains('Background', case=False, na=False)).astype(int)
        
    elif dataset_type == 'nslkdd':
        # NSL-KDD dataset (index-based)
        features['duration'] = pd.to_numeric(df.iloc[:, 0], errors='coerce').fillna(0)
        
        protocol = df.iloc[:, 1].str.lower()
        features['protocol_icmp'] = (protocol == 'icmp').astype(int)
        features['protocol_tcp'] = ((protocol == 'tcp') | (protocol == 'TCP')).astype(int)
        
        features['src_bytes'] = pd.to_numeric(df.iloc[:, 4], errors='coerce').fillna(0)
        features['dst_bytes'] = pd.to_numeric(df.iloc[:, 5], errors='coerce').fillna(0)
        
        label_col = df.iloc[:, -1]
        features['label'] = (label_col != 'normal').astype(int)
    
    # Ensure all features are numeric
    for col in ['duration', 'src_bytes', 'dst_bytes', 'protocol_icmp', 'protocol_tcp']:
        features[col] = pd.to_numeric(features[col], errors='coerce').fillna(0)
    
    return features


def load_dataset_sample(path, dataset_type, sample_size=MAX_SAMPLES_PER_DATASET):
    """Load dataset with sampling for speed"""
    print(f"  Loading {dataset_type} from {os.path.basename(path)}...")
    
    try:
        # For large files, read only first N rows
        if dataset_type == 'nslkdd':
            df = pd.read_csv(path, header=None, nrows=sample_size)
        elif dataset_type == 'cicids':
            df = pd.read_csv(path, nrows=sample_size)
        else:
            df = pd.read_csv(path, nrows=sample_size, skipinitialspace=True)
        
        # Extract features
        features = extract_features_unified(df, dataset_type)
        
        print(f"    Loaded {len(features)} samples")
        return features
        
    except Exception as e:
        print(f"    Error: {e}")
        return pd.DataFrame()


def train_unified_model():
    """Train unified model with sampled data"""
    print("=" * 70)
    print("FAST UNIFIED NETWORK AI MODEL TRAINING")
    print("=" * 70)
    
    all_data = []
    
    # 1. CICIDS2017
    cicids_path = os.path.join(DATASET_DIR, "network_data_cicids", "cicids2017_cleaned.csv")
    if os.path.exists(cicids_path):
        all_data.append(load_dataset_sample(cicids_path, 'cicids', 50000))
    
    # 2. UNSW-NB15
    unsw_files = sorted(glob.glob(os.path.join(DATASET_DIR, "network_data_unsw", "UNSW-NB15_*.csv")))
    for unsw_file in unsw_files[:1]:  # Just use first file
        all_data.append(load_dataset_sample(unsw_file, 'unsw', 30000))
    
    # 3. CTU-13 Botnet
    ctu_files = sorted(glob.glob(os.path.join(DATASET_DIR, "CTU-13-Dataset", "*", "*.binetflow")))
    for ctu_file in ctu_files[:2]:  # Use 2 scenarios
        all_data.append(load_dataset_sample(ctu_file, 'ctu', 20000))
    
    # 4. NSL-KDD
    nsl_train = os.path.join(DATASET_DIR, "network_data_nsl", "KDDTrain+.csv")
    if os.path.exists(nsl_train):
        all_data.append(load_dataset_sample(nsl_train, 'nslkdd', 25000))
    
    # Combine all
    print("\n" + "-" * 70)
    print("Combining datasets...")
    combined = pd.concat(all_data, ignore_index=True)
    
    # Add protocol_udp
    combined['protocol_udp'] = 1 - (combined['protocol_tcp'] + combined['protocol_icmp'])
    combined['protocol_udp'] = combined['protocol_udp'].clip(0, 1)
    
    # Final columns
    feature_cols = ['duration', 'src_bytes', 'dst_bytes', 'protocol_icmp', 'protocol_tcp', 'protocol_udp']
    
    X = combined[feature_cols]
    y = combined['label']
    
    print(f"\nTotal samples: {len(combined)}")
    print(f"Features: {feature_cols}")
    print(f"Normal (0): {sum(y==0)}, Attack (1): {sum(y==1)}")
    
    # Train/test split
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )
    
    # Train model
    print("\n" + "=" * 70)
    print("Training RandomForest...")
    model = RandomForestClassifier(
        n_estimators=50,  # Reduced for speed
        max_depth=15,
        min_samples_split=5,
        min_samples_leaf=2,
        random_state=42,
        class_weight='balanced',
        n_jobs=-1
    )
    
    model.fit(X_train, y_train)
    
    # Evaluate
    y_pred = model.predict(X_test)
    
    print("\n" + "=" * 70)
    print("MODEL PERFORMANCE")
    print("=" * 70)
    print(classification_report(y_test, y_pred, target_names=['Normal', 'Attack']))
    
    # Feature importance
    print("\nFeature Importance:")
    importance = pd.DataFrame({
        'feature': feature_cols,
        'importance': model.feature_importances_
    }).sort_values('importance', ascending=False)
    print(importance.to_string(index=False))
    
    # Save model
    model_dir = "../models"
    os.makedirs(model_dir, exist_ok=True)
    
    # Backup old model
    old_model = os.path.join(model_dir, "network_model.pkl")
    if os.path.exists(old_model):
        backup_path = os.path.join(model_dir, "network_model_backup.pkl")
        joblib.dump(joblib.load(old_model), backup_path)
        print(f"\n✅ Backed up old model to network_model_backup.pkl")
    
    # Save new unified model
    joblib.dump(model, old_model)
    
    import json
    with open(os.path.join(model_dir, "network_feature_names.json"), "w") as f:
        json.dump(feature_cols, f)
    
    print(f"\n{'=' * 70}")
    print(f"✅ Unified model saved to: {old_model}")
    print(f"✅ Feature names saved to network_feature_names.json")
    print(f"{'=' * 70}")
    
    return model, feature_cols


if __name__ == "__main__":
    train_unified_model()
