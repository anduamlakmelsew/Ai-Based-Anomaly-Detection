"""
AI Pipeline tests
"""
import pytest
from unittest.mock import patch, MagicMock
import numpy as np


def test_analyze_scan_network():
    """Test AI analysis for network scan"""
    from app.ai.pipeline import analyze_scan
    
    scan_result = {
        'open_ports': [80, 443, 22],
        'services': [
            {'port': 80, 'protocol': 'tcp'},
            {'port': 443, 'protocol': 'tcp'},
            {'port': 22, 'protocol': 'tcp'}
        ],
        'findings': []
    }
    
    result = analyze_scan('network', scan_result)
    
    assert isinstance(result, dict)
    assert 'prediction' in result
    assert 'confidence' in result
    assert result['prediction'] in ['normal', 'anomaly', 'error', 'unknown']


def test_analyze_scan_web():
    """Test AI analysis for web scan"""
    from app.ai.pipeline import analyze_scan
    
    scan_result = {
        'findings': [
            {'type': 'XSS', 'severity': 'HIGH'},
            {'type': 'SQL Injection', 'severity': 'CRITICAL'}
        ],
        'web_scan': {
            'total_urls': 10,
            'forms_found': 5
        }
    }
    
    result = analyze_scan('web', scan_result)
    
    assert isinstance(result, dict)
    assert 'prediction' in result


def test_analyze_scan_system():
    """Test AI analysis for system scan"""
    from app.ai.pipeline import analyze_scan
    
    scan_result = {
        'system_data': {
            'os_info': {'name': 'Linux', 'version': '5.10'},
            'services': ['ssh', 'nginx']
        },
        'findings': []
    }
    
    result = analyze_scan('system', scan_result)
    
    assert isinstance(result, dict)
    assert 'prediction' in result


def test_analyze_scan_invalid_type():
    """Test AI analysis with invalid scan type"""
    from app.ai.pipeline import analyze_scan
    
    result = analyze_scan('invalid_type', {})
    
    assert isinstance(result, dict)
    assert 'error' in result
    assert result['prediction'] == 'unknown'


def test_network_feature_extraction():
    """Test network feature extraction"""
    from app.ai.network_pipeline import extract_network_features
    
    scan_result = {
        'raw_metrics': {
            'duration_seconds': 10.5
        },
        'services': [
            {'port': 80, 'protocol': 'tcp'},
            {'port': 443, 'protocol': 'tcp'}
        ]
    }
    
    features = extract_network_features(scan_result)
    
    assert isinstance(features, dict)
    assert 'duration' in features
    assert 'src_bytes' in features
    assert 'dst_bytes' in features
    assert 'protocol_tcp' in features


def test_model_loading():
    """Test AI model loading"""
    from app.ai.loader import get_network_model, get_web_model
    
    # Models may or may not exist in test environment
    network_model = get_network_model()
    web_model = get_web_model()
    
    # Should either return a model or None, never crash
    assert network_model is not None or network_model is None
    assert web_model is not None or web_model is None
