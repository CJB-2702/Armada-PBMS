#!/usr/bin/env python3
"""
Test script to verify the events page functionality
"""

import requests
import sys

def test_events_page():
    """Test the events page functionality"""
    base_url = "http://localhost:5001"
    session = requests.Session()
    
    print("Testing Events Page Functionality")
    print("=" * 50)
    
    # Test 1: Login
    print("\n1. Testing login...")
    login_data = {
        'username': 'admin',
        'password': 'admin-password-change-me'
    }
    response = session.post(f"{base_url}/login", data=login_data)
    if response.status_code == 200:
        print("✓ Login successful")
    else:
        print("✗ Login failed")
        return False
    
    # Test 2: Access events page
    print("\n2. Testing events page access...")
    response = session.get(f"{base_url}/core/events")
    if response.status_code == 200:
        print("✓ Events page accessible")
        
        # Check if page contains expected content
        if "Events" in response.text and "Event Type" in response.text:
            print("✓ Events page contains expected content")
        else:
            print("✗ Events page missing expected content")
            return False
    else:
        print(f"✗ Events page access failed: {response.status_code}")
        return False
    
    # Test 3: Check for events in the page
    print("\n3. Testing events display...")
    if "Asset Created" in response.text:
        print("✓ Asset creation events found")
    else:
        print("⚠ No asset creation events found (this might be normal if no assets were created)")
    
    # Test 4: Test main page events link
    print("\n4. Testing main page events link...")
    response = session.get(f"{base_url}/")
    if response.status_code == 200:
        if "/core/events" in response.text:
            print("✓ Main page contains events link")
        else:
            print("✗ Main page missing events link")
            return False
    else:
        print(f"✗ Main page access failed: {response.status_code}")
        return False
    
    print("\n" + "=" * 50)
    print("✓ All events page tests passed!")
    return True

if __name__ == "__main__":
    try:
        success = test_events_page()
        sys.exit(0 if success else 1)
    except requests.exceptions.ConnectionError:
        print("✗ Could not connect to server. Make sure the Flask app is running on port 5001.")
        sys.exit(1)
    except Exception as e:
        print(f"✗ Test failed with error: {e}")
        sys.exit(1) 