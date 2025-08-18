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
    
    logger.debug("=== Phase 4: Basic User Interface and Authentication Test ===")
    
    # Test 1: Check if server is running
    logger.debug("\n1. Testing server availability...")
    try:
        response = requests.get(base_url, timeout=5)
        logger.debug("✅ Server is running")
    except requests.exceptions.RequestException as e:
        logger.debug(f"❌ Server is not running: {e}")
        logger.debug("Please start the server with: python app.py --phase4")
        return False
    
    # Test 2: Check authentication redirect
    logger.debug("\n2. Testing authentication redirect...")
    response = requests.get(base_url, allow_redirects=False)
    if response.status_code == 302 and '/login' in response.headers.get('Location', ''):
        logger.debug("✅ Unauthenticated users are redirected to login")
    else:
        logger.debug("❌ Authentication redirect not working")
        return False
    
    # Test 3: Test login page
    logger.debug("\n3. Testing login page...")
    response = requests.get(f"{base_url}/login")
    if response.status_code == 200 and 'Login' in response.text:
        logger.debug("✅ Login page loads correctly")
    else:
        logger.debug("❌ Login page not working")
        return False
    
    # Test 4: Test login with valid credentials
    logger.debug("\n4. Testing login with valid credentials...")
    session = requests.Session()
    login_data = {
        'username': 'admin',
        'password': 'admin-password-change-me'
    }
    response = session.post(f"{base_url}/login", data=login_data, allow_redirects=False)
    if response.status_code == 302 and response.headers.get('Location') == '/':
        logger.debug("✅ Login successful")
    else:
        logger.debug("❌ Login failed")
        return False
    
    # Test 5: Test authenticated access to home page
    logger.debug("\n5. Testing authenticated home page...")
    response = session.get(base_url)
    if response.status_code == 200 and 'Welcome to Asset Management System' in response.text:
        logger.debug("✅ Home page accessible after login")
    else:
        logger.debug("❌ Home page not accessible after login")
        return False
    
    # Test 6: Test assets list page
    logger.debug("\n6. Testing assets list page...")
    response = session.get(f"{base_url}/assets")
    if response.status_code == 200 and 'Asset List' in response.text:
        logger.debug("✅ Assets list page accessible")
    else:
        logger.debug("❌ Assets list page not accessible")
        return False
    
    # Test 7: Test individual asset view
    logger.debug("\n7. Testing individual asset view...")
    response = session.get(f"{base_url}/assets/1")
    if response.status_code == 200 and 'Asset Details' in response.text:
        logger.debug("✅ Individual asset view accessible")
    else:
        logger.debug("❌ Individual asset view not accessible")
        return False
    
    # Test 8: Test logout
    logger.debug("\n8. Testing logout...")
    response = session.get(f"{base_url}/logout", allow_redirects=False)
    if response.status_code == 302 and '/login' in response.headers.get('Location', ''):
        logger.debug("✅ Logout successful")
    else:
        logger.debug("❌ Logout failed")
        return False
    
    # Test 9: Verify logout actually logged out
    logger.debug("\n9. Verifying logout...")
    response = session.get(base_url, allow_redirects=False)
    if response.status_code == 302 and '/login' in response.headers.get('Location', ''):
        logger.debug("✅ User properly logged out")
    else:
        logger.debug("❌ User not properly logged out")
        return False
    
    logger.debug("\n=== All Phase 4 tests passed! ===")
    logger.debug("✅ Authentication system working")
    logger.debug("✅ User interface accessible")
    logger.debug("✅ Asset management functionality working")
    logger.debug("✅ Session management working")
    
    return True

if __name__ == "__main__":
    logger.debug("Starting Phase 4 tests...")
    logger.debug("Make sure the server is running with: python app.py --phase4")
    logger.debug("Press Enter to continue...")
    input()
    
    success = test_phase4()
    
    if success:
        logger.debug("\n🎉 Phase 4 implementation is complete and working!")
        sys.exit(0)
    else:
        logger.debug("\n❌ Phase 4 tests failed!")
        sys.exit(1) 