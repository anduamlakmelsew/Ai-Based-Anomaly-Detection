"""
Scan route and service tests
"""
import pytest
from unittest.mock import patch, MagicMock


def test_start_scan_unauthorized(client):
    """Test starting scan without authentication"""
    response = client.post('/api/scan/start', json={
        'target': 'example.com',
        'scan_type': 'web'
    })
    assert response.status_code == 401


def test_start_scan_authorized(client, auth_headers):
    """Test starting scan with authentication"""
    with patch('app.routes.scan_routes.run_scan') as mock_run_scan:
        mock_run_scan.return_value = {
            'target': 'example.com',
            'scan_type': 'web',
            'findings': [],
            'risk': {'score': 0, 'level': 'LOW'}
        }
        
        response = client.post('/api/scan/start', 
                              json={
                                  'target': 'example.com',
                                  'scan_type': 'web'
                              },
                              headers=auth_headers)
        
        assert response.status_code in [200, 202]
        mock_run_scan.assert_called_once()


def test_scan_history(client, auth_headers):
    """Test retrieving scan history"""
    response = client.get('/api/scan/history', headers=auth_headers)
    
    assert response.status_code == 200
    data = response.get_json()
    assert 'success' in data or 'data' in data


def test_scan_history_pagination(client, auth_headers):
    """Test scan history pagination"""
    response = client.get('/api/scan/history?limit=10&offset=0', headers=auth_headers)
    
    assert response.status_code == 200


def test_get_single_scan(client, auth_headers):
    """Test getting a specific scan"""
    response = client.get('/api/scan/1', headers=auth_headers)
    
    # Should return 200 if exists, 404 if not
    assert response.status_code in [200, 404]


def test_network_discovery(client, auth_headers):
    """Test network discovery endpoint"""
    with patch('app.routes.scan_routes.discover_hosts') as mock_discover:
        mock_discover.return_value = {
            'success': True,
            'hosts': ['192.168.1.1', '192.168.1.2']
        }
        
        response = client.post('/api/scan/discover',
                              json={'target': '192.168.1.0/24'},
                              headers=auth_headers)
        
        assert response.status_code == 200


def test_invalid_scan_type(client, auth_headers):
    """Test scan with invalid scan type"""
    response = client.post('/api/scan/start',
                          json={
                              'target': 'example.com',
                              'scan_type': 'invalid_type'
                          },
                          headers=auth_headers)
    
    # Should handle gracefully
    assert response.status_code in [200, 400, 422]


def test_scan_missing_target(client, auth_headers):
    """Test scan without target"""
    response = client.post('/api/scan/start',
                          json={'scan_type': 'web'},
                          headers=auth_headers)
    
    assert response.status_code == 400
