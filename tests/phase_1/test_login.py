#!/usr/bin/env python3
"""
Test script to verify admin login functionality
"""

import requests
from bs4 import BeautifulSoup

def test_login():
    """Test the login functionality"""
    base_url = "http://localhost:5000"
    
    logger.debug("Testing Asset Management System Login")
    logger.debug("=" * 50)
    
    # Test 1: Check if home page redirects to login
    logger.debug("\n1. Testing home page redirect...")
    response = requests.get(f"{base_url}/")
    logger.debug(f"Status Code: {response.status_code}")
    logger.debug(f"Redirected to: {response.url}")
    
    # Test 2: Check if login page loads
    logger.debug("\n2. Testing login page...")
    response = requests.get(f"{base_url}/login")
    logger.debug(f"Status Code: {response.status_code}")
    
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        form = soup.find('form')
        if form:
            logger.debug("✓ Login form found")
            logger.debug(f"Form action: {form.get('action', 'N/A')}")
            logger.debug(f"Form method: {form.get('method', 'N/A')}")
        else:
            logger.debug("✗ Login form not found")
    else:
        logger.debug(f"✗ Login page failed to load: {response.status_code}")
    
    # Test 3: Test admin login
    logger.debug("\n3. Testing admin login...")
    login_data = {
        'username': 'admin',
        'password': 'admin123'  # Default password from build system
    }
    
    response = requests.post(f"{base_url}/login", data=login_data, allow_redirects=False)
    logger.debug(f"Login Status Code: {response.status_code}")
    
    if response.status_code == 302:  # Redirect after successful login
        logger.debug("✓ Admin login successful - redirected")
        redirect_url = response.headers.get('Location', '')
        logger.debug(f"Redirected to: {redirect_url}")
        
        # Test 4: Check if we can access the dashboard after login
        logger.debug("\n4. Testing dashboard access...")
        session = requests.Session()
        session.post(f"{base_url}/login", data=login_data)
        
        dashboard_response = session.get(f"{base_url}/")
        logger.debug(f"Dashboard Status Code: {dashboard_response.status_code}")
        
        if dashboard_response.status_code == 200:
            soup = BeautifulSoup(dashboard_response.text, 'html.parser')
            title = soup.find('title')
            if title:
                logger.debug(f"✓ Dashboard loaded: {title.text}")
            else:
                logger.debug("✓ Dashboard loaded (no title found)")
        else:
            logger.debug(f"✗ Dashboard access failed: {dashboard_response.status_code}")
    else:
        logger.debug("✗ Admin login failed")
        logger.debug(f"Response: {response.text[:200]}...")
    
    logger.debug("\n" + "=" * 50)
    logger.debug("Login test completed!")

if __name__ == "__main__":
    test_login() 