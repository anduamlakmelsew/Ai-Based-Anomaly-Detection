"""
Dashboard route tests
"""
import pytest
from datetime import datetime


def test_dashboard_stats(client, auth_headers):
    """Test dashboard stats endpoint"""
    response = client.get('/api/dashboard/stats', headers=auth_headers)
    
    assert response.status_code == 200
    data = response.get_json()
    assert data.get('success') is True
    
    # Check structure
    if 'data' in data:
        stats = data['data']
        assert 'scans' in stats
        assert 'findings' in stats
        assert 'risk' in stats


def test_dashboard_summary(client, auth_headers):
    """Test dashboard summary endpoint"""
    response = client.get('/api/dashboard/summary', headers=auth_headers)
    
    assert response.status_code == 200
    data = response.get_json()
    assert data.get('success') is True


def test_dashboard_activity(client, auth_headers):
    """Test dashboard activity feed"""
    response = client.get('/api/dashboard/activity', headers=auth_headers)
    
    assert response.status_code == 200
    data = response.get_json()
    assert data.get('success') is True
    
    # Should return list of activities
    if 'data' in data:
        assert isinstance(data['data'], list)


def test_dashboard_activity_with_limit(client, auth_headers):
    """Test activity feed with limit parameter"""
    response = client.get('/api/dashboard/activity?limit=5', headers=auth_headers)
    
    assert response.status_code == 200
    data = response.get_json()
    
    if 'data' in data and isinstance(data['data'], list):
        assert len(data['data']) <= 5


def test_ai_insights(client, auth_headers):
    """Test AI insights endpoint"""
    response = client.get('/api/dashboard/ai-insights', headers=auth_headers)
    
    assert response.status_code == 200
    data = response.get_json()
    assert data.get('success') is True
    
    # Check structure
    if 'data' in data:
        insights = data['data']
        assert 'insights' in insights or 'recommendations' in insights


def test_dashboard_unauthorized(client):
    """Test dashboard access without authentication"""
    endpoints = [
        '/api/dashboard/stats',
        '/api/dashboard/summary',
        '/api/dashboard/activity',
        '/api/dashboard/ai-insights'
    ]
    
    for endpoint in endpoints:
        response = client.get(endpoint)
        assert response.status_code == 401, f"Endpoint {endpoint} should require auth"
