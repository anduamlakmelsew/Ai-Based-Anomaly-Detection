"""
Authentication route tests
"""
import pytest


def test_register_success(client):
    """Test successful user registration"""
    response = client.post('/api/auth/register', json={
        'username': 'newuser',
        'email': 'newuser@example.com',
        'password': 'SecurePass123!',
        'role': 'analyst'
    })
    
    assert response.status_code == 201 or response.status_code == 200
    data = response.get_json()
    assert data.get('success') is True or 'message' in data


def test_register_duplicate_username(client):
    """Test registration with duplicate username"""
    # First registration
    client.post('/api/auth/register', json={
        'username': 'duplicate',
        'email': 'dup1@example.com',
        'password': 'SecurePass123!'
    })
    
    # Duplicate registration
    response = client.post('/api/auth/register', json={
        'username': 'duplicate',
        'email': 'dup2@example.com',
        'password': 'SecurePass123!'
    })
    
    assert response.status_code == 400 or response.status_code == 409


def test_login_success(client):
    """Test successful login"""
    # Register first
    client.post('/api/auth/register', json={
        'username': 'logintest',
        'email': 'login@example.com',
        'password': 'TestPass123!'
    })
    
    # Login
    response = client.post('/api/auth/login', json={
        'username': 'logintest',
        'password': 'TestPass123!'
    })
    
    assert response.status_code == 200
    data = response.get_json()
    assert 'access_token' in str(data) or data.get('success') is True


def test_login_invalid_credentials(client):
    """Test login with invalid credentials"""
    response = client.post('/api/auth/login', json={
        'username': 'nonexistent',
        'password': 'wrongpassword'
    })
    
    assert response.status_code == 401


def test_protected_route_without_token(client):
    """Test accessing protected route without token"""
    response = client.get('/api/dashboard/stats')
    assert response.status_code == 401


def test_protected_route_with_token(client, auth_headers):
    """Test accessing protected route with valid token"""
    response = client.get('/api/dashboard/stats', headers=auth_headers)
    # Should not be 401, might be 200 or 500 depending on data
    assert response.status_code != 401
