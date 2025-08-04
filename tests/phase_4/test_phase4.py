#!/usr/bin/env python3
"""
Test script for Phase 4: Basic User Interface and Authentication
"""

import requests
import sys
import time

def test_phase4():
    """Test Phase 4 functionality"""
    base_url = "http://localhost:5000"
    
    print("=== Phase 4: Basic User Interface and Authentication Test ===")
    
    # Test 1: Check if server is running
    print("\n1. Testing server availability...")
    try:
        response = requests.get(base_url, timeout=5)
        print("✅ Server is running")
    except requests.exceptions.RequestException as e:
        print(f"❌ Server is not running: {e}")
        print("Please start the server with: python app.py --phase4")
        return False
    
    # Test 2: Check authentication redirect
    print("\n2. Testing authentication redirect...")
    response = requests.get(base_url, allow_redirects=False)
    if response.status_code == 302 and '/login' in response.headers.get('Location', ''):
        print("✅ Unauthenticated users are redirected to login")
    else:
        print("❌ Authentication redirect not working")
        return False
    
    # Test 3: Test login page
    print("\n3. Testing login page...")
    response = requests.get(f"{base_url}/login")
    if response.status_code == 200 and 'Login' in response.text:
        print("✅ Login page loads correctly")
    else:
        print("❌ Login page not working")
        return False
    
    # Test 4: Test login with valid credentials
    print("\n4. Testing login with valid credentials...")
    session = requests.Session()
    login_data = {
        'username': 'admin',
        'password': 'admin-password-change-me'
    }
    response = session.post(f"{base_url}/login", data=login_data, allow_redirects=False)
    if response.status_code == 302 and response.headers.get('Location') == '/':
        print("✅ Login successful")
    else:
        print("❌ Login failed")
        return False
    
    # Test 5: Test authenticated access to home page
    print("\n5. Testing authenticated home page...")
    response = session.get(base_url)
    if response.status_code == 200 and 'Welcome to Asset Management System' in response.text:
        print("✅ Home page accessible after login")
    else:
        print("❌ Home page not accessible after login")
        return False
    
    # Test 6: Test assets list page
    print("\n6. Testing assets list page...")
    response = session.get(f"{base_url}/assets")
    if response.status_code == 200 and 'Asset List' in response.text:
        print("✅ Assets list page accessible")
    else:
        print("❌ Assets list page not accessible")
        return False
    
    # Test 7: Test individual asset view
    print("\n7. Testing individual asset view...")
    response = session.get(f"{base_url}/assets/1")
    if response.status_code == 200 and 'Asset Details' in response.text:
        print("✅ Individual asset view accessible")
    else:
        print("❌ Individual asset view not accessible")
        return False
    
    # Test 8: Test logout
    print("\n8. Testing logout...")
    response = session.get(f"{base_url}/logout", allow_redirects=False)
    if response.status_code == 302 and '/login' in response.headers.get('Location', ''):
        print("✅ Logout successful")
    else:
        print("❌ Logout failed")
        return False
    
    # Test 9: Verify logout actually logged out
    print("\n9. Verifying logout...")
    response = session.get(base_url, allow_redirects=False)
    if response.status_code == 302 and '/login' in response.headers.get('Location', ''):
        print("✅ User properly logged out")
    else:
        print("❌ User not properly logged out")
        return False
    
    print("\n=== All Phase 4 tests passed! ===")
    print("✅ Authentication system working")
    print("✅ User interface accessible")
    print("✅ Asset management functionality working")
    print("✅ Session management working")
    
    return True

if __name__ == "__main__":
    print("Starting Phase 4 tests...")
    print("Make sure the server is running with: python app.py --phase4")
    print("Press Enter to continue...")
    input()
    
    success = test_phase4()
    
    if success:
        print("\n🎉 Phase 4 implementation is complete and working!")
        sys.exit(0)
    else:
        print("\n❌ Phase 4 tests failed!")
        sys.exit(1) 