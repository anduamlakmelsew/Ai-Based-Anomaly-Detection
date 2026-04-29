"""
Pytest configuration and fixtures for backend tests
"""
import pytest
import os
import sys

# Add the parent directory to path to import app
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app, db
from app.models.user_model import User


@pytest.fixture
def app():
    """Create application for testing"""
    app = create_app()
    app.config.update({
        'TESTING': True,
        'SQLALCHEMY_DATABASE_URI': 'sqlite:///:memory:',
        'JWT_SECRET_KEY': 'test-secret-key',
        'WTF_CSRF_ENABLED': False,
        'DEBUG': False
    })
    
    with app.app_context():
        db.create_all()
        yield app
        db.drop_all()


@pytest.fixture
def client(app):
    """Create test client"""
    return app.test_client()


@pytest.fixture
def runner(app):
    """Create test CLI runner"""
    return app.test_cli_runner()


@pytest.fixture
def auth_headers(client):
    """Create authentication headers with JWT token"""
    # Register a test user
    response = client.post('/api/auth/register', json={
        'username': 'testuser',
        'email': 'test@example.com',
        'password': 'TestPass123!',
        'role': 'analyst'
    })
    
    # Login to get token
    response = client.post('/api/auth/login', json={
        'username': 'testuser',
        'password': 'TestPass123!'
    })
    
    data = response.get_json()
    token = data.get('access_token') or data.get('data', {}).get('access_token')
    
    return {'Authorization': f'Bearer {token}'}


@pytest.fixture
def sample_scan_data():
    """Sample scan data for testing"""
    return {
        'target': 'example.com',
        'scan_type': 'web',
        'findings': [
            {
                'type': 'XSS',
                'severity': 'HIGH',
                'url': 'http://example.com/search',
                'evidence': '<script>alert(1)</script>'
            }
        ],
        'risk': {
            'score': 75,
            'level': 'HIGH'
        }
    }
