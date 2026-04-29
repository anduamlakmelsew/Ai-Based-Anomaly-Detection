"""
network_feature_engineering.py

Production-grade feature engineering pipeline for network intrusion detection.
Transforms unified raw data into engineered features suitable for ML models.
"""

import logging
import numpy as np
import pandas as pd
from typing import Tuple, List, Optional, Dict
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
import joblib
import json
import os

logger = logging.getLogger(__name__)


class NetworkFeatureEngineer:
    """
    Feature engineering pipeline for network intrusion detection.
    
    Creates comprehensive features across multiple domains:
    - Flow features (bytes, packets, duration)
    - Statistical features (means, std, min, max)
    - Behavioral features (connection patterns)
    - TCP flag features
    - Time-based features (rate calculations)
    - Protocol features (encoded categorical)
    """
    
    # Final feature names after engineering
    ENGINEERED_FEATURES = [
        # Flow features
        'duration', 'src_bytes', 'dst_bytes', 'total_bytes',
        'packet_count', 'src_packets', 'dst_packets',
        'bytes_per_second', 'packets_per_second', 'avg_packet_size',
        
        # Statistical features
        'packet_size_mean', 'packet_size_std', 'packet_size_min', 'packet_size_max',
        'inter_arrival_time_mean', 'inter_arrival_time_std',
        
        # Behavioral features
        'connection_count', 'unique_dst_ips', 'unique_dst_ports',
        'same_src_ip_rate', 'same_dst_ip_rate',
        'failed_connections', 'successful_connections',
        'connection_success_rate',
        
        # TCP flags
        'syn_flag_count', 'ack_flag_count', 'rst_flag_count', 'fin_flag_count',
        'syn_to_ack_ratio', 'rst_to_total_ratio',
        
        # Time-based features
        'connections_last_1s', 'connections_last_10s', 'connections_last_60s',
        'bytes_last_10s', 'packets_last_10s',
        'request_rate', 'burst_rate', 'time_since_last_connection',
        
        # Protocol encoded
        'protocol_tcp', 'protocol_udp', 'protocol_icmp',
        
        # Service encoded (top services)
        'service_http', 'service_https', 'service_ssh', 'service_ftp',
        'service_dns', 'service_smtp', 'service_other',
        
        # Flag encoded
        'flag_sf', 'flag_rej', 'flag_s0', 'flag_other',
        
        # Port-based features
        'is_well_known_port', 'is_registered_port', 'is_dynamic_port',
        'port_entropy',
    ]
    
    def __init__(self, fit_mode: bool = True):
        """
        Initialize feature engineer.
        
        Args:
            fit_mode: If True, fit encoders on data. If False, use pre-fitted encoders.
        """
        self.fit_mode = fit_mode
        self.label_encoders: Dict[str, LabelEncoder] = {}
        self.scaler = StandardScaler()
        self.global_stats: Dict = {}
        
        # Fitted flag
        self.is_fitted = False
        
    def fit(self, df: pd.DataFrame) -> 'NetworkFeatureEngineer':
        """
        Fit encoders and compute global statistics.
        
        Args:
            df: Unified dataset DataFrame
            
        Returns:
            self for method chaining
        """
        if not self.fit_mode:
            logger.warning("FeatureEngineer in transform-only mode, skipping fit")
            return self
            
        logger.info("Fitting feature engineering pipeline...")
        
        # Fit protocol encoder
        self.label_encoders['protocol'] = LabelEncoder()
        self.label_encoders['protocol'].fit(df['protocol'].fillna('unknown').unique())
        
        # Fit service encoder (top services only)
        service_counts = df['service'].value_counts()
        top_services = service_counts.head(20).index.tolist()
        self.label_encoders['service'] = LabelEncoder()
        self.label_encoders['service'].fit(top_services + ['other'])
        
        # Fit flag encoder
        self.label_encoders['flag'] = LabelEncoder()
        self.label_encoders['flag'].fit(df['flag'].fillna('').unique())
        
        # Compute global statistics
        self.global_stats = {
            'mean_duration': df['duration'].mean(),
            'std_duration': df['duration'].std(),
            'mean_bytes': df['total_bytes'].mean(),
            'std_bytes': df['total_bytes'].std(),
            'unique_src_ips': df['src_ip'].nunique(),
            'unique_dst_ips': df['dst_ip'].nunique(),
        }
        
        self.is_fitted = True
        logger.info("Feature engineering pipeline fitted successfully")
        
        return self
    
    def transform(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Transform raw unified data into engineered features.
        
        Args:
            df: Unified dataset DataFrame
            
        Returns:
            DataFrame with engineered features
        """
        logger.info(f"Transforming {len(df)} samples...")
        
        features = pd.DataFrame(index=df.index)
        
        # =====================================================
        # FLOW FEATURES
        # =====================================================
        features['duration'] = df['duration'].fillna(0).clip(lower=0)
        features['src_bytes'] = df['src_bytes'].fillna(0).clip(lower=0)
        features['dst_bytes'] = df['dst_bytes'].fillna(0).clip(lower=0)
        features['total_bytes'] = df['total_bytes'].fillna(0).clip(lower=0)
        
        features['src_packets'] = df['src_packets'].fillna(0).clip(lower=0)
        features['dst_packets'] = df['dst_packets'].fillna(0).clip(lower=0)
        features['packet_count'] = df['packet_count'].fillna(0).clip(lower=0)
        
        # Rate features (avoid division by zero)
        features['bytes_per_second'] = np.where(
            features['duration'] > 0,
            features['total_bytes'] / features['duration'],
            0
        )
        features['packets_per_second'] = np.where(
            features['duration'] > 0,
            features['packet_count'] / features['duration'],
            0
        )
        features['avg_packet_size'] = np.where(
            features['packet_count'] > 0,
            features['total_bytes'] / features['packet_count'],
            0
        )
        
        # Clip rate features to avoid infinities
        features['bytes_per_second'] = features['bytes_per_second'].clip(0, 1e9)
        features['packets_per_second'] = features['packets_per_second'].clip(0, 1e6)
        features['avg_packet_size'] = features['avg_packet_size'].clip(0, 65535)
        
        # =====================================================
        # STATISTICAL FEATURES (per-flow estimates)
        # =====================================================
        # Since we have flow-level data, estimate packet size distribution
        features['packet_size_mean'] = features['avg_packet_size']
        features['packet_size_std'] = np.where(
            features['packet_count'] > 1,
            features['packet_size_mean'] * 0.3,  # Estimate 30% std
            0
        )
        features['packet_size_min'] = features['packet_size_mean'] * 0.5
        features['packet_size_max'] = features['packet_size_mean'] * 1.5
        
        # Inter-arrival time estimates
        features['inter_arrival_time_mean'] = np.where(
            features['packet_count'] > 1,
            features['duration'] / (features['packet_count'] - 1),
            0
        )
        features['inter_arrival_time_std'] = features['inter_arrival_time_mean'] * 0.5
        
        # =====================================================
        # BEHAVIORAL FEATURES (per-source aggregation)
        # =====================================================
        # These require aggregation by source IP
        src_stats = df.groupby('src_ip').agg({
            'dst_ip': 'nunique',
            'dst_port': 'nunique',
            'label': 'count',
        }).reset_index()
        src_stats.columns = ['src_ip', 'unique_dst_ips', 'unique_dst_ports', 'connection_count']
        
        # Merge back
        features = features.merge(src_stats, left_on=df['src_ip'], right_on='src_ip', how='left')
        features = features.drop(columns=['src_ip'], errors='ignore')
        
        # Fill NaN for rows that couldn't be merged
        features['unique_dst_ips'] = features['unique_dst_ips'].fillna(1)
        features['unique_dst_ports'] = features['unique_dst_ports'].fillna(1)
        features['connection_count'] = features['connection_count'].fillna(1)
        
        # Same IP rates (simplified)
        features['same_src_ip_rate'] = 1.0  # All connections from same src in this flow
        features['same_dst_ip_rate'] = 1.0 / features['unique_dst_ips'].clip(lower=1)
        
        # Failed/successful connections (based on RST flag or label)
        features['failed_connections'] = (
            (df['rst_flag'] > 0) | 
            (df['flag'].str.contains('REJ', na=False))
        ).astype(int)
        
        # Estimate successful connections (SYN+ACK but no RST)
        features['successful_connections'] = (
            (df['syn_flag'] > 0) & 
            (df['ack_flag'] > 0) & 
            (df['rst_flag'] == 0)
        ).astype(int)
        
        # Success rate
        features['connection_success_rate'] = np.where(
            features['connection_count'] > 0,
            features['successful_connections'] / features['connection_count'],
            0.5  # Default 50% if no info
        )
        
        # =====================================================
        # TCP FLAG FEATURES
        # =====================================================
        features['syn_flag_count'] = df['syn_flag'].fillna(0).astype(int)
        features['ack_flag_count'] = df['ack_flag'].fillna(0).astype(int)
        features['rst_flag_count'] = df['rst_flag'].fillna(0).astype(int)
        features['fin_flag_count'] = df['fin_flag'].fillna(0).astype(int)
        
        # Ratios
        flag_total = (
            features['syn_flag_count'] + 
            features['ack_flag_count'] + 
            features['rst_flag_count'] + 
            features['fin_flag_count']
        ).clip(lower=1)
        
        features['syn_to_ack_ratio'] = np.where(
            features['ack_flag_count'] > 0,
            features['syn_flag_count'] / features['ack_flag_count'],
            features['syn_flag_count']
        ).clip(0, 10)
        
        features['rst_to_total_ratio'] = features['rst_flag_count'] / flag_total
        
        # =====================================================
        # TIME-BASED FEATURES (sliding windows)
        # =====================================================
        # Sort by start_time for window calculations
        df_sorted = df.sort_values('start_time')
        
        # Rolling window counts (simplified - in production use proper time windows)
        # For now, use index-based windows as approximation
        window_1s = max(1, len(df) // 1000) if len(df) > 1000 else 1
        window_10s = window_1s * 10
        window_60s = window_1s * 60
        
        features['connections_last_1s'] = 1  # Per-flow approximation
        features['connections_last_10s'] = df.groupby(
            (df.index // window_10s).astype(int)
        )['label'].transform('count').fillna(1)
        features['connections_last_60s'] = df.groupby(
            (df.index // window_60s).astype(int)
        )['label'].transform('count').fillna(1)
        
        # Bytes/packets in last 10s
        features['bytes_last_10s'] = features['total_bytes']  # Per-flow
        features['packets_last_10s'] = features['packet_count']  # Per-flow
        
        # Rates
        features['request_rate'] = features['packets_per_second']
        features['burst_rate'] = features['bytes_per_second'] / 1000  # KB/s
        features['time_since_last_connection'] = features['inter_arrival_time_mean']
        
        # =====================================================
        # PROTOCOL FEATURES (one-hot encoded)
        # =====================================================
        protocol = df['protocol'].fillna('tcp').str.lower()
        features['protocol_tcp'] = (protocol == 'tcp').astype(int)
        features['protocol_udp'] = (protocol == 'udp').astype(int)
        features['protocol_icmp'] = (protocol == 'icmp').astype(int)
        
        # =====================================================
        # SERVICE FEATURES (one-hot encoded, top services)
        # =====================================================
        service = df['service'].fillna('unknown').str.lower()
        features['service_http'] = service.isin(['http', 'www']).astype(int)
        features['service_https'] = (service == 'https').astype(int)
        features['service_ssh'] = (service == 'ssh').astype(int)
        features['service_ftp'] = service.isin(['ftp', 'ftps']).astype(int)
        features['service_dns'] = (service == 'dns').astype(int)
        features['service_smtp'] = service.isin(['smtp', 'smtps']).astype(int)
        features['service_other'] = (
            ~service.isin(['http', 'www', 'https', 'ssh', 'ftp', 'ftps', 'dns', 'smtp', 'smtps'])
        ).astype(int)
        
        # =====================================================
        # FLAG FEATURES (one-hot encoded)
        # =====================================================
        flag = df['flag'].fillna('')
        features['flag_sf'] = (flag == 'SF').astype(int)  # SYN-FIN (normal completion)
        features['flag_rej'] = flag.str.contains('REJ', na=False).astype(int)  # Rejected
        features['flag_s0'] = (flag == 'S0').astype(int)  # SYN only (half-open)
        features['flag_other'] = (
            ~flag.isin(['SF', 'S0']) & ~flag.str.contains('REJ', na=False)
        ).astype(int)
        
        # =====================================================
        # PORT-BASED FEATURES
        # =====================================================
        dst_port = pd.to_numeric(df['dst_port'], errors='coerce').fillna(0).astype(int)
        
        features['is_well_known_port'] = (dst_port <= 1023).astype(int)
        features['is_registered_port'] = ((dst_port > 1023) & (dst_port <= 49151)).astype(int)
        features['is_dynamic_port'] = (dst_port > 49151).astype(int)
        
        # Port entropy (simplified - use count of unique ports per src)
        port_entropy = df.groupby('src_ip')['dst_port'].nunique()
        features['port_entropy'] = df['src_ip'].map(port_entropy).fillna(1)
        
        # =====================================================
        # CLEANUP AND VALIDATION
        # =====================================================
        # Fill any remaining NaN values
        features = features.fillna(0)
        
        # Replace inf values
        features = features.replace([np.inf, -np.inf], 0)
        
        # Ensure all expected features are present
        for col in self.ENGINEERED_FEATURES:
            if col not in features.columns:
                logger.warning(f"Missing feature: {col}, filling with 0")
                features[col] = 0
        
        # Reorder columns to match expected order
        features = features[self.ENGINEERED_FEATURES]
        
        logger.info(f"Feature engineering complete. Output shape: {features.shape}")
        
        return features
    
    def fit_transform(self, df: pd.DataFrame) -> pd.DataFrame:
        """Fit and transform in one call."""
        return self.fit(df).transform(df)
    
    def save(self, path: str):
        """Save fitted feature engineering artifacts."""
        artifacts = {
            'label_encoders': self.label_encoders,
            'global_stats': self.global_stats,
            'engineered_features': self.ENGINEERED_FEATURES,
            'is_fitted': self.is_fitted,
        }
        joblib.dump(artifacts, path)
        logger.info(f"Feature engineering artifacts saved to {path}")
        
        # Also save feature names as JSON
        json_path = path.replace('.pkl', '_features.json')
        with open(json_path, 'w') as f:
            json.dump(self.ENGINEERED_FEATURES, f, indent=2)
        logger.info(f"Feature names saved to {json_path}")
    
    def load(self, path: str):
        """Load fitted feature engineering artifacts."""
        artifacts = joblib.load(path)
        self.label_encoders = artifacts['label_encoders']
        self.global_stats = artifacts['global_stats']
        self.is_fitted = artifacts['is_fitted']
        logger.info(f"Feature engineering artifacts loaded from {path}")
        return self


class FeaturePreprocessor:
    """
    Preprocessing pipeline for network features.
    Handles scaling and normalization.
    """
    
    def __init__(self):
        self.scaler = StandardScaler()
        self.is_fitted = False
        self.feature_names: List[str] = []
        
    def fit(self, X: pd.DataFrame) -> 'FeaturePreprocessor':
        """Fit the scaler."""
        self.feature_names = list(X.columns)
        self.scaler.fit(X)
        self.is_fitted = True
        logger.info(f"Preprocessor fitted on {len(self.feature_names)} features")
        return self
    
    def transform(self, X: pd.DataFrame) -> np.ndarray:
        """Transform features."""
        if not self.is_fitted:
            raise RuntimeError("Preprocessor not fitted. Call fit() first.")
        
        # Ensure column order matches
        X = X[self.feature_names]
        return self.scaler.transform(X)
    
    def fit_transform(self, X: pd.DataFrame) -> np.ndarray:
        """Fit and transform."""
        return self.fit(X).transform(X)
    
    def save(self, path: str):
        """Save preprocessor."""
        joblib.dump({
            'scaler': self.scaler,
            'feature_names': self.feature_names,
            'is_fitted': self.is_fitted,
        }, path)
        logger.info(f"Preprocessor saved to {path}")
    
    def load(self, path: str):
        """Load preprocessor."""
        data = joblib.load(path)
        self.scaler = data['scaler']
        self.feature_names = data['feature_names']
        self.is_fitted = data['is_fitted']
        logger.info(f"Preprocessor loaded from {path}")
        return self


def extract_features_from_scan_result(scan_result: dict) -> pd.DataFrame:
    """
    Extract features from a scan result for real-time inference.
    This adapts the unified schema to the scan result format.
    
    Args:
        scan_result: Network scan result dictionary
        
    Returns:
        DataFrame with engineered features (single row)
    """
    # Extract raw metrics
    raw_metrics = scan_result.get('raw_metrics', {})
    services = scan_result.get('services', [])
    
    # Build unified row
    unified = {}
    
    # Basic flow features
    unified['duration'] = raw_metrics.get('duration_seconds', 0)
    
    # Estimate bytes from services
    src_bytes = raw_metrics.get('src_bytes', 0)
    dst_bytes = raw_metrics.get('dst_bytes', 0)
    
    # If not available, estimate from port types
    if src_bytes == 0 and dst_bytes == 0:
        for svc in services:
            port = svc.get('port', 0)
            if port in [80, 443, 8080]:
                src_bytes += 1000
                dst_bytes += 2000
            elif port == 22:
                src_bytes += 500
                dst_bytes += 800
            elif port in [21, 23]:
                src_bytes += 300
                dst_bytes += 400
            else:
                src_bytes += 200
                dst_bytes += 300
    
    unified['src_bytes'] = src_bytes
    unified['dst_bytes'] = dst_bytes
    unified['total_bytes'] = src_bytes + dst_bytes
    
    # Packets (estimate from bytes/typical MTU)
    mtu = 1500
    unified['src_packets'] = max(1, src_bytes / mtu)
    unified['dst_packets'] = max(1, dst_bytes / mtu)
    unified['packet_count'] = unified['src_packets'] + unified['dst_packets']
    
    # IPs and ports
    unified['src_ip'] = scan_result.get('target', '0.0.0.0')
    unified['dst_ip'] = '0.0.0.0'  # Scan target
    unified['src_port'] = 0
    unified['dst_port'] = services[0]['port'] if services else 0
    
    # Protocol
    protocols = [svc.get('protocol', 'tcp').lower() for svc in services]
    protocol_counts = {}
    for p in protocols:
        protocol_counts[p] = protocol_counts.get(p, 0) + 1
    
    dominant_protocol = max(protocol_counts, key=protocol_counts.get) if protocol_counts else 'tcp'
    unified['protocol'] = dominant_protocol
    
    # Service inference
    unified['service'] = services[0].get('service', 'unknown') if services else 'unknown'
    
    # Flags (scan results don't typically have these, estimate)
    unified['syn_flag'] = 1 if services else 0
    unified['ack_flag'] = 1 if services else 0
    unified['rst_flag'] = 0
    unified['fin_flag'] = 0
    unified['flag'] = 'SF' if services else ''
    
    # Time
    unified['start_time'] = pd.Timestamp.now()
    
    # Labels (not used for inference)
    unified['label'] = 0
    unified['attack_category'] = 'Unknown'
    
    # Create DataFrame
    df = pd.DataFrame([unified])
    
    # Apply feature engineering
    engineer = NetworkFeatureEngineer(fit_mode=False)
    features = engineer.transform(df)
    
    return features


# Convenience function
def engineer_features(df: pd.DataFrame, fit: bool = True) -> Tuple[pd.DataFrame, NetworkFeatureEngineer]:
    """
    Engineer features from unified dataset.
    
    Args:
        df: Unified dataset DataFrame
        fit: Whether to fit the feature engineer (True for training, False for inference)
        
    Returns:
        Tuple of (features DataFrame, feature engineer instance)
    """
    engineer = NetworkFeatureEngineer(fit_mode=fit)
    
    if fit:
        features = engineer.fit_transform(df)
    else:
        features = engineer.transform(df)
    
    return features, engineer


if __name__ == "__main__":
    # Test feature engineering
    logging.basicConfig(level=logging.INFO)
    
    # Create sample data
    sample_data = {
        'duration': [1.5, 0.5, 10.0],
        'src_bytes': [1000, 500, 50000],
        'dst_bytes': [2000, 1000, 100000],
        'total_bytes': [3000, 1500, 150000],
        'src_packets': [10, 5, 100],
        'dst_packets': [20, 10, 200],
        'packet_count': [30, 15, 300],
        'src_ip': ['192.168.1.1', '192.168.1.2', '10.0.0.1'],
        'dst_ip': ['8.8.8.8', '1.1.1.1', '192.168.1.1'],
        'src_port': [12345, 54321, 8080],
        'dst_port': [80, 443, 22],
        'protocol': ['tcp', 'udp', 'tcp'],
        'service': ['http', 'dns', 'ssh'],
        'syn_flag': [1, 0, 1],
        'ack_flag': [1, 0, 1],
        'rst_flag': [0, 0, 0],
        'fin_flag': [0, 0, 0],
        'flag': ['SF', '', 'SF'],
        'start_time': pd.date_range('2024-01-01', periods=3, freq='s'),
        'label': [0, 0, 1],
        'attack_category': ['Normal', 'Normal', 'DoS'],
    }
    
    df = pd.DataFrame(sample_data)
    
    # Test feature engineering
    engineer = NetworkFeatureEngineer(fit_mode=True)
    features = engineer.fit_transform(df)
    
    print("\n" + "=" * 60)
    print("FEATURE ENGINEERING TEST")
    print("=" * 60)
    print(f"Input shape: {df.shape}")
    print(f"Output shape: {features.shape}")
    print(f"\nEngineered features ({len(features.columns)}):")
    for i, col in enumerate(features.columns, 1):
        print(f"  {i:2d}. {col}")
    
    print(f"\nFeature statistics:")
    print(features.describe())
