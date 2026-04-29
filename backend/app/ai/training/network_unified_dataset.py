"""
network_unified_dataset.py

Unified dataset loader for network intrusion detection.
Auto-discovers and loads datasets from network/ and botnet/ directories.
Supports CTU-13, CICIDS-2017, UNSW-NB15, NSL-KDD and other formats.
"""

import os
import glob
import logging
import pandas as pd
import numpy as np
from typing import Tuple, Optional, List, Dict, Set
from dataclasses import dataclass
from pathlib import Path

logger = logging.getLogger(__name__)

# Dataset base path - actual location
DATASET_ROOT = "/home/andu/AI_Baseline_Assessment_Scanner/backend/app/ai/network and botnet  datasets"


@dataclass
class DatasetConfig:
    """Configuration for a dataset loader."""
    name: str
    path_patterns: List[str]
    loader_func: callable


class NetworkDatasetLoader:
    """
    Unified loader for all network intrusion detection datasets.
    Maps dataset-specific fields to unified schema.
    """
    
    # Unified schema columns (raw features before engineering)
    UNIFIED_SCHEMA = [
        'duration', 'src_bytes', 'dst_bytes', 'total_bytes',
        'src_packets', 'dst_packets', 'packet_count',
        'src_ip', 'dst_ip', 'src_port', 'dst_port',
        'protocol', 'service', 'flag',
        'syn_flag', 'ack_flag', 'rst_flag', 'fin_flag',
        'start_time', 'label', 'attack_category'
    ]
    
    # Attack category mapping for multi-class classification
    ATTACK_CATEGORIES = {
        'normal': 'Normal',
        'benign': 'Normal',
        'background': 'Normal',
        'dos': 'DoS',
        'ddos': 'DoS',
        'denial of service': 'DoS',
        'probe': 'Probe',
        'portscan': 'Probe',
        'scanning': 'Probe',
        'r2l': 'R2L',
        'remote to local': 'R2L',
        'u2r': 'U2R',
        'user to root': 'U2R',
        'botnet': 'Botnet',
        'web attack': 'Web Attack',
        'sql injection': 'Web Attack',
        'xss': 'Web Attack',
        'ftp-patator': 'Brute Force',
        'ssh-patator': 'Brute Force',
        'brute force': 'Brute Force',
    }
    
    def __init__(self, max_samples_per_dataset: Optional[int] = None):
        """
        Initialize the dataset loader.
        
        Args:
            max_samples_per_dataset: Limit samples per dataset for testing
        """
        self.max_samples = max_samples_per_dataset
        self.mappings_log = []
        
    def _discover_datasets(self) -> Dict[str, List[Dict]]:
        """
        Auto-discover all dataset files in the dataset root.
        
        Returns:
            Dict mapping dataset_type to list of file info dicts
        """
        logger.info("=" * 60)
        logger.info("DISCOVERING DATASETS")
        logger.info("=" * 60)
        logger.info(f"Scanning: {DATASET_ROOT}")
        
        discovered = {
            'cicids': [],
            'unsw': [],
            'nsl_kdd': [],
            'ctu13': [],
            'unknown': []
        }
        
        if not os.path.exists(DATASET_ROOT):
            logger.error(f"Dataset root not found: {DATASET_ROOT}")
            return discovered
        
        # Walk through all subdirectories
        for root, dirs, files in os.walk(DATASET_ROOT):
            # Skip __pycache__ and hidden dirs
            dirs[:] = [d for d in dirs if not d.startswith('.') and d != '__pycache__']
            
            for file in files:
                file_lower = file.lower()
                filepath = os.path.join(root, file)
                rel_path = os.path.relpath(filepath, DATASET_ROOT)
                
                # Check file extensions
                is_csv = file_lower.endswith('.csv')
                is_binetflow = file_lower.endswith('.binetflow')
                is_parquet = file_lower.endswith('.parquet')
                is_json = file_lower.endswith('.json')
                
                if not (is_csv or is_binetflow or is_parquet or is_json):
                    continue
                
                # Infer dataset type from path and filename
                dataset_type = 'unknown'
                
                # Check folder names in path
                path_parts = rel_path.lower().split(os.sep)
                
                if any('cicids' in p or 'cic-ids' in p or 'cic' in p for p in path_parts):
                    dataset_type = 'cicids'
                elif any('unsw' in p or 'unsw-nb15' in p for p in path_parts):
                    dataset_type = 'unsw'
                elif any('nsl' in p or 'kdd' in p or 'nsl-kdd' in p for p in path_parts):
                    dataset_type = 'nsl_kdd'
                elif any('ctu' in p or 'ctu-13' in p or 'botnet' in p for p in path_parts):
                    dataset_type = 'ctu13'
                
                # Double-check with filename
                if dataset_type == 'unknown':
                    if 'cicids' in file_lower or 'cic' in file_lower:
                        dataset_type = 'cicids'
                    elif 'unsw' in file_lower:
                        dataset_type = 'unsw'
                    elif 'kdd' in file_lower:
                        dataset_type = 'nsl_kdd'
                    elif 'capture' in file_lower or '.binetflow' in file_lower:
                        dataset_type = 'ctu13'
                
                file_info = {
                    'path': filepath,
                    'relative_path': rel_path,
                    'filename': file,
                    'type': dataset_type,
                    'format': 'csv' if is_csv else ('binetflow' if is_binetflow else ('parquet' if is_parquet else 'json'))
                }
                
                discovered[dataset_type].append(file_info)
                logger.info(f"  [{dataset_type.upper()}] {rel_path}")
        
        # Summary
        logger.info("\n" + "-" * 60)
        logger.info("DISCOVERY SUMMARY:")
        for dtype, files in discovered.items():
            if files:
                logger.info(f"  {dtype}: {len(files)} files")
        logger.info("-" * 60)
        
        return discovered
    
    def _load_file(self, file_info: Dict, nrows: Optional[int] = None) -> Optional[pd.DataFrame]:
        """
        Load a single dataset file based on its format.
        
        Args:
            file_info: File info dict from _discover_datasets
            nrows: Maximum number of rows to read (for sampling)
            
        Returns:
            DataFrame or None if loading failed
        """
        path = file_info['path']
        fmt = file_info['format']
        dtype = file_info['type']
        
        try:
            if fmt == 'csv':
                # Try different encodings and separators
                for encoding in ['utf-8', 'latin-1', 'iso-8859-1', 'cp1252']:
                    try:
                        # Try to detect separator
                        with open(path, 'r', encoding=encoding, errors='ignore') as f:
                            first_line = f.readline()
                            if '|' in first_line:
                                sep = '|'
                            elif ';' in first_line:
                                sep = ';'
                            elif '\t' in first_line:
                                sep = '\t'
                            else:
                                sep = ','
                        
                        # Read with nrows limit if specified
                        if nrows:
                            df = pd.read_csv(path, encoding=encoding, sep=sep, low_memory=False, nrows=nrows)
                            logger.info(f"    Loaded CSV (sampled): {os.path.basename(path)} ({len(df)} rows)")
                        else:
                            df = pd.read_csv(path, encoding=encoding, sep=sep, low_memory=False)
                            logger.info(f"    Loaded CSV: {os.path.basename(path)} ({len(df)} rows)")
                        return df
                    except UnicodeDecodeError:
                        continue
                    except Exception as e:
                        logger.debug(f"    Failed with encoding {encoding}: {e}")
                        continue
                        
            elif fmt == 'binetflow':
                # CTU-13 format - comma-separated with specific columns
                if nrows:
                    df = pd.read_csv(path, sep=',', low_memory=False, nrows=nrows)
                    logger.info(f"    Loaded Binetflow (sampled): {os.path.basename(path)} ({len(df)} rows)")
                else:
                    df = pd.read_csv(path, sep=',', low_memory=False)
                    logger.info(f"    Loaded Binetflow: {os.path.basename(path)} ({len(df)} rows)")
                return df
                
            elif fmt == 'parquet':
                df = pd.read_parquet(path)
                if nrows and len(df) > nrows:
                    df = df.sample(n=nrows, random_state=42)
                    logger.info(f"    Loaded Parquet (sampled): {os.path.basename(path)} ({len(df)} rows)")
                else:
                    logger.info(f"    Loaded Parquet: {os.path.basename(path)} ({len(df)} rows)")
                return df
                
            elif fmt == 'json':
                if nrows:
                    df = pd.read_json(path, lines=True, nrows=nrows)
                    logger.info(f"    Loaded JSON (sampled): {os.path.basename(path)} ({len(df)} rows)")
                else:
                    df = pd.read_json(path, lines=True)
                    logger.info(f"    Loaded JSON: {os.path.basename(path)} ({len(df)} rows)")
                return df
                
        except Exception as e:
            logger.warning(f"    Failed to load {os.path.basename(path)}: {e}")
            return None
        
        return None
    
    def load_all_datasets(self) -> pd.DataFrame:
        """
        Load and combine all available datasets.
        
        Returns:
            Combined DataFrame with unified schema
        """
        logger.info("\n" + "=" * 60)
        logger.info("LOADING UNIFIED NETWORK DATASETS")
        logger.info("=" * 60)
        
        # Discover all datasets
        discovered = self._discover_datasets()
        
        all_data = []
        
        # Define loaders for each dataset type
        dataset_loaders = [
            ('cicids', self._normalize_cicids),
            ('unsw', self._normalize_unsw),
            ('nsl_kdd', self._normalize_nslkdd),
            ('ctu13', self._normalize_ctu13),
            ('unknown', self._normalize_generic),
        ]
        
        for dtype, normalizer in dataset_loaders:
            files = discovered.get(dtype, [])
            if not files:
                continue
            
            logger.info(f"\n Loading {dtype.upper()} datasets ({len(files)} files)...")
            
            for file_info in files:
                try:
                    # Load the file with optional row limit for efficiency
                    raw_df = self._load_file(file_info, nrows=self.max_samples)
                    if raw_df is None or len(raw_df) == 0:
                        logger.warning(f"    Skipping empty file: {file_info['filename']}")
                        continue
                    
                    # Normalize to unified schema
                    normalized = normalizer(raw_df, file_info)
                    
                    if normalized is not None and len(normalized) > 0:
                        normalized['dataset_source'] = dtype
                        normalized['source_file'] = file_info['filename']
                        all_data.append(normalized)
                        logger.info(f"    Normalized {len(normalized)} rows from {file_info['filename']}")
                    
                except Exception as e:
                    logger.error(f"    Failed to process {file_info['filename']}: {e}")
                    import traceback
                    logger.debug(traceback.format_exc())
                    continue
        
        # Handle case where no datasets loaded
        if not all_data:
            logger.warning("=" * 60)
            logger.warning("NO DATASETS COULD BE LOADED!")
            logger.warning("Returning empty DataFrame with unified schema")
            logger.warning("=" * 60)
            
            # Return empty DataFrame with correct columns
            empty_df = pd.DataFrame(columns=self.UNIFIED_SCHEMA + ['dataset_source', 'source_file'])
            return empty_df
        
        # Combine all datasets
        logger.info("\n" + "=" * 60)
        logger.info("COMBINING DATASETS")
        logger.info("=" * 60)
        
        combined = pd.concat(all_data, ignore_index=True)
        
        logger.info(f"Combined dataset shape: {combined.shape}")
        logger.info(f"Dataset sources:")
        for source, count in combined['dataset_source'].value_counts().items():
            logger.info(f"  - {source}: {count} samples")
        
        return combined
    
    def _normalize_cicids(self, raw_df: pd.DataFrame, file_info: Dict) -> Optional[pd.DataFrame]:
        """
        Normalize CICIDS-2017 data to unified schema.
        """
        logger.debug(f"Normalizing CICIDS: {file_info['filename']}")
        
        unified = pd.DataFrame()
        
        # Try to find columns (case insensitive)
        raw_cols_lower = {c.lower(): c for c in raw_df.columns}
        
        # Duration (convert from ms to seconds if needed)
        if 'flow duration' in raw_cols_lower:
            unified['duration'] = pd.to_numeric(raw_df[raw_cols_lower['flow duration']], errors='coerce') / 1000.0
        else:
            unified['duration'] = 0.0
        unified['duration'] = unified['duration'].fillna(0).clip(lower=0)
        
        # Bytes
        if 'total length of fwd packets' in raw_cols_lower:
            unified['src_bytes'] = pd.to_numeric(raw_df[raw_cols_lower['total length of fwd packets']], errors='coerce').fillna(0)
        elif 'fwd packet length total' in raw_cols_lower:
            unified['src_bytes'] = pd.to_numeric(raw_df[raw_cols_lower['fwd packet length total']], errors='coerce').fillna(0)
        else:
            unified['src_bytes'] = 0
            
        if 'total length of bwd packets' in raw_cols_lower:
            unified['dst_bytes'] = pd.to_numeric(raw_df[raw_cols_lower['total length of bwd packets']], errors='coerce').fillna(0)
        elif 'bwd packet length total' in raw_cols_lower:
            unified['dst_bytes'] = pd.to_numeric(raw_df[raw_cols_lower['bwd packet length total']], errors='coerce').fillna(0)
        else:
            unified['dst_bytes'] = 0
            
        unified['total_bytes'] = unified['src_bytes'] + unified['dst_bytes']
        
        # Packets
        if 'total fwd packets' in raw_cols_lower:
            unified['src_packets'] = pd.to_numeric(raw_df[raw_cols_lower['total fwd packets']], errors='coerce').fillna(0)
        elif 'total forward packets' in raw_cols_lower:
            unified['src_packets'] = pd.to_numeric(raw_df[raw_cols_lower['total forward packets']], errors='coerce').fillna(0)
        else:
            unified['src_packets'] = 0
            
        if 'total backward packets' in raw_cols_lower:
            unified['dst_packets'] = pd.to_numeric(raw_df[raw_cols_lower['total backward packets']], errors='coerce').fillna(0)
        elif 'total bwd packets' in raw_cols_lower:
            unified['dst_packets'] = pd.to_numeric(raw_df[raw_cols_lower['total bwd packets']], errors='coerce').fillna(0)
        else:
            unified['dst_packets'] = 0
            
        unified['packet_count'] = unified['src_packets'] + unified['dst_packets']
        
        # IPs and ports
        if 'source ip' in raw_cols_lower:
            unified['src_ip'] = raw_df[raw_cols_lower['source ip']].astype(str)
        elif 'src ip' in raw_cols_lower:
            unified['src_ip'] = raw_df[raw_cols_lower['src ip']].astype(str)
        else:
            unified['src_ip'] = '0.0.0.0'
            
        if 'destination ip' in raw_cols_lower:
            unified['dst_ip'] = raw_df[raw_cols_lower['destination ip']].astype(str)
        elif 'dst ip' in raw_cols_lower:
            unified['dst_ip'] = raw_df[raw_cols_lower['dst ip']].astype(str)
        else:
            unified['dst_ip'] = '0.0.0.0'
        
        if 'source port' in raw_cols_lower:
            unified['src_port'] = pd.to_numeric(raw_df[raw_cols_lower['source port']], errors='coerce').fillna(0).astype(int)
        elif 'src port' in raw_cols_lower:
            unified['src_port'] = pd.to_numeric(raw_df[raw_cols_lower['src port']], errors='coerce').fillna(0).astype(int)
        else:
            unified['src_port'] = 0
            
        if 'destination port' in raw_cols_lower:
            unified['dst_port'] = pd.to_numeric(raw_df[raw_cols_lower['destination port']], errors='coerce').fillna(0).astype(int)
        elif 'dst port' in raw_cols_lower:
            unified['dst_port'] = pd.to_numeric(raw_df[raw_cols_lower['dst port']], errors='coerce').fillna(0).astype(int)
        else:
            unified['dst_port'] = 0
        
        # Protocol
        if 'protocol' in raw_cols_lower:
            proto = raw_df[raw_cols_lower['protocol']].astype(str).str.lower()
            proto_map = {'6': 'tcp', '17': 'udp', '1': 'icmp', 'tcp': 'tcp', 'udp': 'udp', 'icmp': 'icmp'}
            unified['protocol'] = proto.map(proto_map).fillna('tcp')
        else:
            unified['protocol'] = 'tcp'
        
        # Service (inferred from port)
        unified['service'] = unified['dst_port'].apply(self._port_to_service)
        
        # Flags (CICIDS doesn't have raw flags, estimate from packet counts)
        unified['syn_flag'] = (unified['packet_count'] > 0).astype(int)
        unified['ack_flag'] = (unified['packet_count'] > 1).astype(int)
        unified['rst_flag'] = 0
        unified['fin_flag'] = 0
        unified['flag'] = 'SF'
        
        # Timestamp
        if 'timestamp' in raw_cols_lower:
            unified['start_time'] = pd.to_datetime(raw_df[raw_cols_lower['timestamp']], errors='coerce')
        elif 'flow start time' in raw_cols_lower:
            unified['start_time'] = pd.to_datetime(raw_df[raw_cols_lower['flow start time']], errors='coerce')
        else:
            unified['start_time'] = pd.Timestamp.now()
        
        # Labels
        if 'label' in raw_cols_lower:
            raw_label = raw_df[raw_cols_lower['label']].astype(str).str.lower()
            unified['label'] = (raw_label != 'benign').astype(int)
            unified['attack_category'] = raw_label.apply(self._normalize_attack_category)
        else:
            unified['label'] = 0
            unified['attack_category'] = 'Normal'
        
        return unified
    
    def _normalize_generic(self, df: pd.DataFrame, file_info: Dict) -> Optional[pd.DataFrame]:
        """
        Generic normalizer for unknown dataset formats.
        Attempts to map columns by name similarity.
        """
        logger.debug(f"Applying generic normalization to {file_info['filename']}")
        
        cols_lower = {c.lower(): c for c in df.columns}
        
        unified = {}
        
        # Try to find duration
        duration_cols = [c for c in cols_lower if 'duration' in c or 'time' in c]
        if duration_cols:
            unified['duration'] = pd.to_numeric(df[cols_lower[duration_cols[0]]], errors='coerce').fillna(0)
        else:
            unified['duration'] = 0
        
        # Try to find bytes
        src_bytes_cols = [c for c in cols_lower if 'src' in c and ('byte' in c or 'bytes' in c)]
        dst_bytes_cols = [c for c in cols_lower if 'dst' in c and ('byte' in c or 'bytes' in c)]
        
        if src_bytes_cols:
            unified['src_bytes'] = pd.to_numeric(df[cols_lower[src_bytes_cols[0]]], errors='coerce').fillna(0)
        else:
            unified['src_bytes'] = 0
            
        if dst_bytes_cols:
            unified['dst_bytes'] = pd.to_numeric(df[cols_lower[dst_bytes_cols[0]]], errors='coerce').fillna(0)
        else:
            unified['dst_bytes'] = 0
        
        unified['total_bytes'] = unified['src_bytes'] + unified['dst_bytes']
        
        # Packets
        pkt_cols = [c for c in cols_lower if 'packet' in c or 'pkt' in c]
        if pkt_cols:
            unified['packet_count'] = pd.to_numeric(df[cols_lower[pkt_cols[0]]], errors='coerce').fillna(0)
        else:
            unified['packet_count'] = 0
        unified['src_packets'] = unified['packet_count'] // 2
        unified['dst_packets'] = unified['packet_count'] // 2
        
        # IPs
        src_ip_cols = [c for c in cols_lower if 'src' in c and ('ip' in c or 'addr' in c)]
        dst_ip_cols = [c for c in cols_lower if 'dst' in c and ('ip' in c or 'addr' in c)]
        unified['src_ip'] = df[src_ip_cols[0]].astype(str) if src_ip_cols else '0.0.0.0'
        unified['dst_ip'] = df[dst_ip_cols[0]].astype(str) if dst_ip_cols else '0.0.0.0'
        
        # Ports
        src_port_cols = [c for c in cols_lower if 'src' in c and 'port' in c]
        dst_port_cols = [c for c in cols_lower if 'dst' in c and 'port' in c]
        unified['src_port'] = pd.to_numeric(df[cols_lower[src_port_cols[0]]], errors='coerce').fillna(0).astype(int) if src_port_cols else 0
        unified['dst_port'] = pd.to_numeric(df[cols_lower[dst_port_cols[0]]], errors='coerce').fillna(0).astype(int) if dst_port_cols else 0
        
        # Protocol
        proto_cols = [c for c in cols_lower if 'proto' in c]
        unified['protocol'] = df[proto_cols[0]].astype(str).str.lower() if proto_cols else 'tcp'
        
        # Service
        svc_cols = [c for c in cols_lower if 'service' in c or 'svc' in c]
        unified['service'] = df[svc_cols[0]].astype(str).str.lower() if svc_cols else 'unknown'
        
        # Flags
        unified['syn_flag'] = 0
        unified['ack_flag'] = 0
        unified['rst_flag'] = 0
        unified['fin_flag'] = 0
        
        flag_cols = [c for c in cols_lower if 'flag' in c]
        if flag_cols:
            unified['flag'] = df[flag_cols[0]].astype(str)
        else:
            unified['flag'] = ''
        
        # Time
        time_cols = [c for c in cols_lower if 'time' in c or 'date' in c or 'ts' in c or 'start' in c]
        if time_cols:
            unified['start_time'] = pd.to_datetime(df[time_cols[0]], errors='coerce')
        else:
            unified['start_time'] = pd.Timestamp.now()
        
        # Labels - try to find label column
        label_cols = [c for c in cols_lower if 'label' in c]
        if label_cols:
            raw_labels = df[label_cols[0]].astype(str).str.lower()
            # Try to infer binary labels
            unified['label'] = raw_labels.apply(lambda x: 0 if any(n in x for n in ['normal', 'benign', '0']) else 1)
            
            # Attack category
            unified['attack_category'] = raw_labels.apply(self._normalize_attack_category)
        else:
            unified['label'] = 0
            unified['attack_category'] = 'Unknown'
        
        return pd.DataFrame(unified)
    
    def _normalize_nslkdd(self, raw_df: pd.DataFrame, file_info: Dict) -> Optional[pd.DataFrame]:
        """
        Normalize NSL-KDD data to unified schema.
        """
        logger.debug(f"Normalizing NSL-KDD: {file_info['filename']}")
        
        df = raw_df
        unified = {}
        
        # NSL-KDD has specific column structure
        # Protocol is column 1 (0-indexed: 1)
        unified['protocol'] = df.iloc[:, 1].astype(str).str.lower()
        
        # Service is column 2
        unified['service'] = df.iloc[:, 2].astype(str).str.lower()
        
        # Flag is column 3
        unified['flag'] = df.iloc[:, 3].astype(str)
        unified['syn_flag'] = unified['flag'].apply(lambda x: 1 if 'S' in str(x) else 0)
        unified['ack_flag'] = unified['flag'].apply(lambda x: 1 if 'A' in str(x) else 0)
        unified['rst_flag'] = unified['flag'].apply(lambda x: 1 if 'R' in str(x) else 0)
        unified['fin_flag'] = unified['flag'].apply(lambda x: 1 if 'F' in str(x) else 0)
        
        # Bytes
        unified['src_bytes'] = pd.to_numeric(df.iloc[:, 4], errors='coerce').fillna(0)
        unified['dst_bytes'] = pd.to_numeric(df.iloc[:, 5], errors='coerce').fillna(0)
        unified['total_bytes'] = unified['src_bytes'] + unified['dst_bytes']
        
        # NSL-KDD doesn't have packet counts directly but has wrong_fragment, urgent
        # Use src_bytes/100 as rough packet estimate
        unified['src_packets'] = unified['src_bytes'] / 100
        unified['dst_packets'] = unified['dst_bytes'] / 100
        unified['packet_count'] = unified['src_packets'] + unified['dst_packets']
        
        # Duration - column 0
        unified['duration'] = pd.to_numeric(df.iloc[:, 0], errors='coerce').fillna(0)
        
        # IP addresses not directly in NSL-KDD (has land, logged_in, is_host_login, is_guest_login)
        unified['src_ip'] = '0.0.0.0'
        unified['dst_ip'] = '0.0.0.0'
        unified['src_port'] = 0
        unified['dst_port'] = 0
        
        unified['start_time'] = pd.Timestamp.now()
        
        # Labels - last column is label, second-to-last is difficulty level
        raw_label = df.iloc[:, -2].astype(str).str.strip().str.lower()
        unified['label'] = (raw_label != 'normal').astype(int)
        unified['attack_category'] = raw_label.apply(self._normalize_attack_category)
        
        return pd.DataFrame(unified)
    
    def _normalize_unsw(self, raw_df: pd.DataFrame, file_info: Dict) -> Optional[pd.DataFrame]:
        """
        Normalize UNSW-NB15 data to unified schema.
        """
        logger.debug(f"Normalizing UNSW-NB15: {file_info['filename']}")
        
        df = raw_df
        n_rows = len(df)
        cols_lower = {c.lower(): c for c in df.columns}
        unified = {}
        
        # Duration
        if 'dur' in cols_lower or 'duration' in cols_lower:
            dur_col = cols_lower.get('dur') or cols_lower.get('duration')
            unified['duration'] = pd.to_numeric(df[dur_col], errors='coerce').fillna(0)
        else:
            unified['duration'] = pd.Series([0] * n_rows)
        
        # Bytes
        if 'sbytes' in cols_lower:
            unified['src_bytes'] = pd.to_numeric(df[cols_lower['sbytes']], errors='coerce').fillna(0)
        else:
            unified['src_bytes'] = pd.Series([0] * n_rows)
            
        if 'dbytes' in cols_lower:
            unified['dst_bytes'] = pd.to_numeric(df[cols_lower['dbytes']], errors='coerce').fillna(0)
        else:
            unified['dst_bytes'] = pd.Series([0] * n_rows)
            
        unified['total_bytes'] = unified['src_bytes'] + unified['dst_bytes']
        
        # Packets
        if 'spkts' in cols_lower:
            unified['src_packets'] = pd.to_numeric(df[cols_lower['spkts']], errors='coerce').fillna(0)
        else:
            unified['src_packets'] = unified['src_bytes'] / 100  # Estimate
            
        if 'dpkts' in cols_lower:
            unified['dst_packets'] = pd.to_numeric(df[cols_lower['dpkts']], errors='coerce').fillna(0)
        else:
            unified['dst_packets'] = unified['dst_bytes'] / 100  # Estimate
            
        unified['packet_count'] = unified['src_packets'] + unified['dst_packets']
        
        # IPs
        if 'srcip' in cols_lower or 'srcip' in cols_lower:
            ip_col = cols_lower.get('srcip')
            unified['src_ip'] = df[ip_col].astype(str)
        else:
            unified['src_ip'] = pd.Series(['0.0.0.0'] * n_rows)
            
        if 'dstip' in cols_lower or 'dstip' in cols_lower:
            ip_col = cols_lower.get('dstip')
            unified['dst_ip'] = df[ip_col].astype(str)
        else:
            unified['dst_ip'] = pd.Series(['0.0.0.0'] * n_rows)
        
        # Ports
        if 'sport' in cols_lower:
            unified['src_port'] = pd.to_numeric(df[cols_lower['sport']], errors='coerce').fillna(0).astype(int)
        else:
            unified['src_port'] = pd.Series([0] * n_rows)
            
        if 'dsport' in cols_lower or 'dport' in cols_lower:
            port_col = cols_lower.get('dsport') or cols_lower.get('dport')
            unified['dst_port'] = pd.to_numeric(df[port_col], errors='coerce').fillna(0).astype(int)
        else:
            unified['dst_port'] = pd.Series([0] * n_rows)
        
        # Protocol
        if 'proto' in cols_lower or 'protocol' in cols_lower:
            proto_col = cols_lower.get('proto') or cols_lower.get('protocol')
            unified['protocol'] = df[proto_col].astype(str).str.lower()
        else:
            unified['protocol'] = pd.Series(['tcp'] * n_rows)
        
        # Service - use the service column or infer from dst_port
        if 'service' in cols_lower:
            unified['service'] = df[cols_lower['service']].astype(str).str.lower()
        else:
            # Create series by applying port_to_service to each dst_port
            unified['service'] = unified['dst_port'].apply(lambda p: self._port_to_service(int(p)) if pd.notna(p) else 'unknown')
        
        # Flags - UNSW has state column
        if 'state' in cols_lower:
            unified['flag'] = df[cols_lower['state']].astype(str)
        else:
            unified['flag'] = pd.Series([''] * n_rows)
        unified['syn_flag'] = pd.Series([0] * n_rows)
        unified['ack_flag'] = pd.Series([0] * n_rows)
        unified['rst_flag'] = pd.Series([0] * n_rows)
        unified['fin_flag'] = pd.Series([0] * n_rows)
        
        # Time
        unified['start_time'] = pd.Series([pd.Timestamp.now()] * n_rows)
        
        # Labels
        if 'label' in cols_lower or 'attack_cat' in cols_lower:
            label_col = cols_lower.get('label') or cols_lower.get('attack_cat')
            raw_label = df[label_col].astype(str).str.lower()
            unified['label'] = raw_label.apply(lambda x: 0 if any(n in x for n in ['normal', 'benign', '0', 'backdoor']) else 1)
            unified['attack_category'] = raw_label.apply(self._normalize_attack_category)
        else:
            unified['label'] = pd.Series([0] * n_rows)
            unified['attack_category'] = pd.Series(['Normal'] * n_rows)
        
        return pd.DataFrame(unified)
    
    def _normalize_ctu13(self, raw_df: pd.DataFrame, file_info: Dict) -> Optional[pd.DataFrame]:
        """
        Normalize CTU-13 binetflow data to unified schema.
        """
        logger.debug(f"Normalizing CTU-13: {file_info['filename']}")
        
        df = raw_df
        unified = {}
        
        # CTU-13 binetflow has specific columns
        # Typical columns: StartTime, Dur, Proto, SrcAddr, Sport, Dir, DstAddr, Dport, State, sTos, dTos, TotPkts, TotBytes, SrcBytes, Label
        
        cols_lower = {c.lower(): c for c in df.columns}
        
        # Duration
        if 'dur' in cols_lower or 'duration' in cols_lower:
            dur_col = cols_lower.get('dur') or cols_lower.get('duration')
            unified['duration'] = pd.to_numeric(df[dur_col], errors='coerce').fillna(0)
        else:
            unified['duration'] = 0
        
        # Protocol
        if 'proto' in cols_lower:
            unified['protocol'] = df[cols_lower['proto']].astype(str).str.lower()
        else:
            unified['protocol'] = 'tcp'
        
        # IPs
        if 'srcaddr' in cols_lower or 'src ip' in cols_lower or 'source' in cols_lower:
            ip_col = cols_lower.get('srcaddr') or cols_lower.get('src ip') or cols_lower.get('source')
            unified['src_ip'] = df[ip_col].astype(str)
        else:
            unified['src_ip'] = '0.0.0.0'
            
        if 'dstaddr' in cols_lower or 'dst ip' in cols_lower or 'dest' in cols_lower or 'destination' in cols_lower:
            ip_col = (cols_lower.get('dstaddr') or cols_lower.get('dst ip') or 
                     cols_lower.get('dest') or cols_lower.get('destination'))
            unified['dst_ip'] = df[ip_col].astype(str)
        else:
            unified['dst_ip'] = '0.0.0.0'
        
        # Ports
        if 'sport' in cols_lower:
            unified['src_port'] = pd.to_numeric(df[cols_lower['sport']], errors='coerce').fillna(0).astype(int)
        else:
            unified['src_port'] = 0
            
        if 'dport' in cols_lower:
            unified['dst_port'] = pd.to_numeric(df[cols_lower['dport']], errors='coerce').fillna(0).astype(int)
        else:
            unified['dst_port'] = 0
        
        # Bytes
        if 'srcbytes' in cols_lower or 'src_bytes' in cols_lower:
            bytes_col = cols_lower.get('srcbytes') or cols_lower.get('src_bytes')
            unified['src_bytes'] = pd.to_numeric(df[bytes_col], errors='coerce').fillna(0)
        else:
            unified['src_bytes'] = 0
            
        if 'totbytes' in cols_lower or 'total_bytes' in cols_lower or 'totbytes' in cols_lower:
            bytes_col = (cols_lower.get('totbytes') or cols_lower.get('total_bytes') or 
                        cols_lower.get('totbytes'))
            tot_bytes = pd.to_numeric(df[bytes_col], errors='coerce').fillna(0)
            unified['dst_bytes'] = tot_bytes - unified['src_bytes']
        else:
            unified['dst_bytes'] = 0
            
        unified['total_bytes'] = unified['src_bytes'] + unified['dst_bytes']
        
        # Packets
        if 'totpkts' in cols_lower or 'total_packets' in cols_lower:
            pkt_col = cols_lower.get('totpkts') or cols_lower.get('total_packets')
            unified['packet_count'] = pd.to_numeric(df[pkt_col], errors='coerce').fillna(0)
        else:
            unified['packet_count'] = unified['total_bytes'] / 100  # Estimate
        
        unified['src_packets'] = unified['packet_count'] / 2
        unified['dst_packets'] = unified['packet_count'] / 2
        
        # Service
        unified['service'] = unified['dst_port'].apply(self._port_to_service)
        
        # Flags from state
        if 'state' in cols_lower:
            unified['flag'] = df[cols_lower['state']].astype(str)
        else:
            unified['flag'] = ''
        unified['syn_flag'] = 0
        unified['ack_flag'] = 0
        unified['rst_flag'] = 0
        unified['fin_flag'] = 0
        
        # Time
        if 'starttime' in cols_lower or 'start_time' in cols_lower or 'time' in cols_lower:
            time_col = (cols_lower.get('starttime') or cols_lower.get('start_time') or 
                       cols_lower.get('time'))
            unified['start_time'] = pd.to_datetime(df[time_col], errors='coerce')
        else:
            unified['start_time'] = pd.Timestamp.now()
        
        # Labels
        if 'label' in cols_lower:
            raw_label = df[cols_lower['label']].astype(str).str.lower()
            # CTU-13 labels are like "Botnet", "Normal", "Background"
            unified['label'] = raw_label.apply(lambda x: 1 if 'botnet' in x or 'attack' in x else 0)
            unified['attack_category'] = raw_label.apply(self._normalize_attack_category)
        else:
            unified['label'] = 0
            unified['attack_category'] = 'Normal'
        
        return pd.DataFrame(unified)
    
    def _port_to_service(self, port: int) -> str:
        """Map port number to service name."""
        return self._infer_service(port)
    
    def _infer_service(self, port: int) -> str:
        """Infer service name from port number."""
        service_map = {
            80: 'http', 443: 'https', 8080: 'http-proxy',
            22: 'ssh', 21: 'ftp', 23: 'telnet',
            25: 'smtp', 110: 'pop3', 143: 'imap',
            53: 'dns', 123: 'ntp', 161: 'snmp',
            3306: 'mysql', 5432: 'postgresql', 1433: 'mssql',
            27017: 'mongodb', 6379: 'redis', 9200: 'elasticsearch',
        }
        return service_map.get(int(port), 'unknown')
    
    def _build_flag(self, syn: int, ack: int, rst: int, fin: int) -> str:
        """Build flag string from individual flags."""
        flags = []
        if syn: flags.append('S')
        if ack: flags.append('A')
        if rst: flags.append('R')
        if fin: flags.append('F')
        return ''.join(flags) if flags else ''
    
    def _normalize_attack_category(self, raw_label: str) -> str:
        """Normalize raw attack labels to unified categories."""
        if pd.isna(raw_label):
            return 'Unknown'
        
        raw = str(raw_label).strip().lower()
        
        # Direct mappings
        for key, category in self.ATTACK_CATEGORIES.items():
            if key in raw:
                return category
        
        # Pattern matching
        if any(x in raw for x in ['dos', 'ddos', 'flood', 'ping', 'smurf', 'teardrop', 'apache', 'back']):
            return 'DoS'
        if any(x in raw for x in ['scan', 'satan', 'ipsweep', 'portsweep', 'nmap', 'mscan', 'saint']):
            return 'Probe'
        if any(x in raw for x in ['guess', 'ftp', 'imap', 'phf', 'multihop', 'warez', 'spy']):
            return 'R2L'
        if any(x in raw for x in ['buffer', 'rootkit', 'perl', 'loadmodule', 'xterm', 'ps']):
            return 'U2R'
        
        return 'Unknown'
    
    def get_binary_labels(self, df: pd.DataFrame) -> np.ndarray:
        """Extract binary labels (0=Normal, 1=Attack)."""
        return df['label'].values.astype(int)
    
    def get_multiclass_labels(self, df: pd.DataFrame) -> np.ndarray:
        """
        Extract multi-class labels.
        Returns encoded labels for: Normal, DoS, Probe, R2L, U2R, Other
        """
        category_mapping = {
            'Normal': 0,
            'DoS': 1,
            'Probe': 2,
            'R2L': 3,
            'U2R': 4,
        }
        
        # Map categories, default to 5 (Other) for unknown
        labels = df['attack_category'].map(
            lambda x: category_mapping.get(x, 5)
        ).values.astype(int)
        
        return labels
    
    def get_multiclass_names(self) -> List[str]:
        """Get multi-class category names."""
        return ['Normal', 'DoS', 'Probe', 'R2L', 'U2R', 'Other']


# Convenience function
def load_unified_network_dataset(max_samples_per_dataset: Optional[int] = None) -> pd.DataFrame:
    """
    Load and unify all network intrusion detection datasets.
    
    Args:
        max_samples_per_dataset: Limit samples per dataset (for testing)
        
    Returns:
        Unified DataFrame with standardized columns
    """
    loader = NetworkDatasetLoader(max_samples_per_dataset=max_samples_per_dataset)
    return loader.load_all_datasets()


if __name__ == "__main__":
    # Test the loader
    logging.basicConfig(level=logging.INFO)
    
    try:
        df = load_unified_network_dataset(max_samples_per_dataset=10000)
        
        print("\n" + "=" * 60)
        print("DATASET SUMMARY")
        print("=" * 60)
        print(f"Total samples: {len(df)}")
        print(f"\nColumns: {list(df.columns)}")
        print(f"\nBinary class distribution:")
        print(df['label'].value_counts())
        print(f"\nAttack category distribution:")
        print(df['attack_category'].value_counts())
        print(f"\nDataset source distribution:")
        print(df['dataset_source'].value_counts())
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
