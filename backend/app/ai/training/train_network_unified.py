"""
Unified Network AI Training
Combines CICIDS2017, UNSW-NB15, CTU-13 Botnet, and NSL-KDD datasets
Maps to unified features: duration, src_bytes, dst_bytes, protocol_icmp, protocol_tcp, protocol_udp
"""
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, confusion_matrix
import joblib
import os
import glob
import warnings
warnings.filterwarnings('ignore')

# Dataset paths
DATASET_DIR = "/home/andu/AI_Baseline_Assessment_Scanner/backend/app/ai/network and botnet  datasets"

def extract_cicids_features(df):
    """Extract unified features from CICIDS2017 dataset"""
    features = pd.DataFrame()
    features['duration'] = pd.to_numeric(df['Flow Duration'], errors='coerce').fillna(0) / 1000000  # Convert to seconds
    
    # Calculate src_bytes and dst_bytes from forward and backward packets
    fwd_bytes = pd.to_numeric(df['Total Length of Fwd Packets'], errors='coerce').fillna(0)
    # Handle case where Bwd Packets column might not exist
    if 'Total Length of Bwd Packets' in df.columns:
        bwd_bytes = pd.to_numeric(df['Total Length of Bwd Packets'], errors='coerce').fillna(0)
    else:
        bwd_bytes = pd.Series([0] * len(df), index=df.index)
    
    features['src_bytes'] = fwd_bytes
    features['dst_bytes'] = bwd_bytes
    
    # Protocol mapping - CICIDS doesn't have protocol column directly
    # Infer from Destination Port or use a default
    features['protocol_icmp'] = 0  # CICIDS primarily TCP/UDP
    features['protocol_tcp'] = 1
    features['dst_port'] = pd.to_numeric(df['Destination Port'], errors='coerce').fillna(0)
    
    # Label: BENIGN = 0 (normal), anything else = 1 (attack)
    features['label'] = (df['Attack Type'] != 'BENIGN').astype(int)
    
    return features


def extract_unsw_features(df):
    """Extract unified features from UNSW-NB15 dataset"""
    features = pd.DataFrame()
    features['duration'] = pd.to_numeric(df['Dur'], errors='coerce').fillna(0)
    features['src_bytes'] = pd.to_numeric(df['SrcBytes'], errors='coerce').fillna(0)
    
    # Calculate dst_bytes
    total_bytes = pd.to_numeric(df['TotBytes'], errors='coerce').fillna(0)
    features['dst_bytes'] = total_bytes - features['src_bytes']
    
    # Protocol one-hot encoding
    proto = df['Proto'].str.lower()
    features['protocol_icmp'] = (proto == 'icmp').astype(int)
    features['protocol_tcp'] = (proto == 'tcp').astype(int)
    
    # Label: normal = 0, anything else = 1
    label_col = df.columns[-1]  # Usually the last column is label
    features['label'] = (df[label_col] != 'normal').astype(int)
    
    return features


def extract_ctu_features(df):
    """Extract unified features from CTU-13 botnet dataset"""
    features = pd.DataFrame()
    features['duration'] = pd.to_numeric(df['Dur'], errors='coerce').fillna(0)
    features['src_bytes'] = pd.to_numeric(df['SrcBytes'], errors='coerce').fillna(0)
    
    # Calculate dst_bytes
    total_bytes = pd.to_numeric(df['TotBytes'], errors='coerce').fillna(0)
    features['dst_bytes'] = total_bytes - features['src_bytes']
    
    # Protocol one-hot encoding
    proto = df['Proto'].str.lower()
    features['protocol_icmp'] = (proto == 'icmp').astype(int)
    features['protocol_tcp'] = (proto == 'tcp').astype(int)
    
    # Label: Background = 0 (normal), botnet/attack = 1
    label_col = df.columns[-1]
    features['label'] = (~df[label_col].str.contains('Background', case=False, na=False)).astype(int)
    
    return features


def extract_nslkdd_features(df):
    """Extract unified features from NSL-KDD dataset"""
    # NSL-KDD has specific structure
    features = pd.DataFrame()
    
    # Map NSL-KDD columns (index-based mapping)
    features['duration'] = pd.to_numeric(df.iloc[:, 0], errors='coerce').fillna(0)
    
    # Protocol (column 1) - categorical
    protocol = df.iloc[:, 1].str.lower()
    features['protocol_icmp'] = (protocol == 'icmp').astype(int)
    features['protocol_tcp'] = (protocol == 'tcp').astype(int)
    
    # src_bytes (column 4), dst_bytes (column 5)
    features['src_bytes'] = pd.to_numeric(df.iloc[:, 4], errors='coerce').fillna(0)
    features['dst_bytes'] = pd.to_numeric(df.iloc[:, 5], errors='coerce').fillna(0)
    
    # Label (last column) - normal = normal, everything else = attack
    label_col = df.iloc[:, -1]
    features['label'] = (label_col != 'normal').astype(int)
    
    return features


def load_and_combine_datasets():
    """Load all datasets and combine into unified feature set"""
    all_data = []
    
    print("Loading datasets...")
    
    # 1. CICIDS2017
    cicids_path = os.path.join(DATASET_DIR, "network_data_cicids", "cicids2017_cleaned.csv")
    if os.path.exists(cicids_path):
        print(f"  Loading CICIDS2017 from {cicids_path}...")
        df_cicids = pd.read_csv(cicids_path)
        cicids_features = extract_cicids_features(df_cicids)
        all_data.append(cicids_features)
        print(f"    Loaded {len(cicids_features)} samples")
    
    # 2. UNSW-NB15
    unsw_files = glob.glob(os.path.join(DATASET_DIR, "network_data_unsw", "UNSW-NB15_*.csv"))
    for unsw_file in unsw_files[:2]:  # Use first 2 files to limit memory
        print(f"  Loading UNSW from {unsw_file}...")
        df_unsw = pd.read_csv(unsw_file, skipinitialspace=True)
        unsw_features = extract_unsw_features(df_unsw)
        all_data.append(unsw_features)
        print(f"    Loaded {len(unsw_features)} samples")
    
    # 3. CTU-13 Botnet
    ctu_files = glob.glob(os.path.join(DATASET_DIR, "CTU-13-Dataset", "*", "*.binetflow"))
    for ctu_file in ctu_files[:3]:  # Use first 3 scenarios
        print(f"  Loading CTU-13 from {ctu_file}...")
        try:
            df_ctu = pd.read_csv(ctu_file, skipinitialspace=True)
            ctu_features = extract_ctu_features(df_ctu)
            all_data.append(ctu_features)
            print(f"    Loaded {len(ctu_features)} samples")
        except Exception as e:
            print(f"    Error loading {ctu_file}: {e}")
    
    # 4. NSL-KDD
    nsl_train = os.path.join(DATASET_DIR, "network_data_nsl", "KDDTrain+.csv")
    if os.path.exists(nsl_train):
        print(f"  Loading NSL-KDD from {nsl_train}...")
        df_nsl = pd.read_csv(nsl_train, header=None)
        nsl_features = extract_nslkdd_features(df_nsl)
        all_data.append(nsl_features)
        print(f"    Loaded {len(nsl_features)} samples")
    
    # Combine all datasets
    print("\nCombining datasets...")
    combined = pd.concat(all_data, ignore_index=True)
    
    # Add protocol_udp (calculated from tcp and icmp)
    combined['protocol_udp'] = 1 - (combined['protocol_tcp'] + combined['protocol_icmp'])
    combined['protocol_udp'] = combined['protocol_udp'].clip(0, 1)
    
    # Final feature set (matching expected model input)
    final_features = [
        'duration', 'src_bytes', 'dst_bytes',
        'protocol_icmp', 'protocol_tcp', 'protocol_udp',
        'label'
    ]
    
    # Clean data
    combined = combined[final_features].fillna(0)
    
    print(f"\nCombined dataset shape: {combined.shape}")
    print(f"Class distribution:\n{combined['label'].value_counts()}")
    
    return combined


def train_unified_model():
    """Train unified RandomForest model on all datasets"""
    print("=" * 60)
    print("UNIFIED NETWORK AI MODEL TRAINING")
    print("=" * 60)
    
    # Load and combine data
    data = load_and_combine_datasets()
    
    # Prepare features and labels
    feature_cols = ['duration', 'src_bytes', 'dst_bytes', 'protocol_icmp', 'protocol_tcp', 'protocol_udp']
    X = data[feature_cols]
    y = data['label']
    
    print(f"\nTraining with {len(data)} samples")
    print(f"Features: {feature_cols}")
    print(f"Normal samples: {sum(y==0)}")
    print(f"Attack samples: {sum(y==1)}")
    
    # Split data
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )
    
    print(f"\nTrain set: {len(X_train)} samples")
    print(f"Test set: {len(X_test)} samples")
    
    # Train RandomForest
    print("\nTraining RandomForest model...")
    model = RandomForestClassifier(
        n_estimators=100,
        max_depth=20,
        min_samples_split=10,
        min_samples_leaf=5,
        random_state=42,
        class_weight='balanced',
        n_jobs=-1
    )
    
    model.fit(X_train, y_train)
    
    # Evaluate
    y_pred = model.predict(X_test)
    
    print("\n" + "=" * 60)
    print("MODEL PERFORMANCE")
    print("=" * 60)
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
    
    model_path = os.path.join(model_dir, "network_model_unified.pkl")
    joblib.dump(model, model_path)
    
    # Save feature names
    import json
    with open(os.path.join(model_dir, "network_feature_names.json"), "w") as f:
        json.dump(feature_cols, f)
    
    print(f"\n{'=' * 60}")
    print(f"✅ Model saved to: {model_path}")
    print(f"✅ Feature names saved")
    print(f"{'=' * 60}")
    
    return model, feature_cols


if __name__ == "__main__":
    train_unified_model()
