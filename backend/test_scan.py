#!/usr/bin/env python3
"""
Test script to verify scan endpoint works
"""
import requests
import json

BASE_URL = "http://127.0.0.1:5001"

def get_auth_token():
    """Login and get JWT token"""
    response = requests.post(
        f"{BASE_URL}/api/auth/login",
        json={"username": "admin", "password": "admin123"}
    )
    if response.status_code == 200:
        return response.json().get("access_token")
    else:
        print(f"Login failed: {response.status_code} - {response.text}")
        return None

def test_scan():
    """Test the scan endpoint"""
    token = get_auth_token()
    if not token:
        print("❌ Failed to get auth token")
        return
    
    print(f"✅ Got auth token: {token[:20]}...")
    
    # Test scan endpoint
    headers = {"Authorization": f"Bearer {token}"}
    scan_data = {
        "target": "127.0.0.1",
        "scan_type": "network",
        "sync": True  # Run synchronously for testing
    }
    
    print(f"\n📡 Starting scan: {scan_data}")
    response = requests.post(
        f"{BASE_URL}/api/scan/start",
        json=scan_data,
        headers=headers
    )
    
    print(f"\n📊 Response Status: {response.status_code}")
    print(f"📊 Response Body:")
    print(json.dumps(response.json(), indent=2))
    
    if response.status_code == 200:
        print("\n✅ SCAN ENDPOINT WORKS!")
    else:
        print("\n❌ SCAN ENDPOINT FAILED!")

if __name__ == "__main__":
    test_scan()
