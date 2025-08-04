#!/usr/bin/env python3
"""
Simple test script to verify login and home page functionality
"""

import requests
import sys

def test_login_and_home():
    """Test login and home page functionality"""
    base_url = "http://localhost:5001"
    session = requests.Session()
    
    print("Testing Asset Management System Login and Home Page")
    print("=" * 50)
    
    # Test 1: Access home page without login (should redirect to login)
    print("\n1. Testing home page access without login...")
    response = session.get(f"{base_url}/")
    if "Login - Asset Management System" in response.text:
        print("✓ Home page correctly redirects to login when not authenticated")
    else:
        print("✗ Home page access test failed")
        return False
    
    # Test 2: Login with correct credentials
    print("\n2. Testing login with correct credentials...")
    login_data = {
        'username': 'admin',
        'password': 'admin-password-change-me'
    }
    response = session.post(f"{base_url}/login", data=login_data)
    if response.status_code == 200 and "Asset Management System - Home" in response.text:
        print("✓ Login successful")
    else:
        print("✗ Login failed")
        return False
    
    # Test 3: Access home page after login
    print("\n3. Testing home page access after login...")
    response = session.get(f"{base_url}/")
    if "Asset Management System - Home" in response.text:
        print("✓ Home page accessible after login")
    else:
        print("✗ Home page access after login failed")
        return False
    
    # Test 4: Logout
    print("\n4. Testing logout...")
    response = session.get(f"{base_url}/logout")
    if response.status_code == 200:
        print("✓ Logout successful")
    else:
        print("✗ Logout failed")
        return False
    
    # Test 5: Verify home page is protected after logout
    print("\n5. Testing home page protection after logout...")
    response = session.get(f"{base_url}/")
    if "Login - Asset Management System" in response.text:
        print("✓ Home page correctly protected after logout")
    else:
        print("✗ Home page protection test failed")
        return False
    
    print("\n" + "=" * 50)
    print("✓ All tests passed! Login and home page are working correctly.")
    return True

if __name__ == "__main__":
    try:
        success = test_login_and_home()
        sys.exit(0 if success else 1)
    except requests.exceptions.ConnectionError:
        print("✗ Could not connect to server. Make sure the Flask app is running on port 5001.")
        sys.exit(1)
    except Exception as e:
        print(f"✗ Test failed with error: {e}")
        sys.exit(1) 