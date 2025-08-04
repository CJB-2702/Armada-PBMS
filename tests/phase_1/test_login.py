#!/usr/bin/env python3
"""
Test script to verify admin login functionality
"""

import requests
from bs4 import BeautifulSoup

def test_login():
    """Test the login functionality"""
    base_url = "http://localhost:5000"
    
    print("Testing Asset Management System Login")
    print("=" * 50)
    
    # Test 1: Check if home page redirects to login
    print("\n1. Testing home page redirect...")
    response = requests.get(f"{base_url}/")
    print(f"Status Code: {response.status_code}")
    print(f"Redirected to: {response.url}")
    
    # Test 2: Check if login page loads
    print("\n2. Testing login page...")
    response = requests.get(f"{base_url}/login")
    print(f"Status Code: {response.status_code}")
    
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        form = soup.find('form')
        if form:
            print("✓ Login form found")
            print(f"Form action: {form.get('action', 'N/A')}")
            print(f"Form method: {form.get('method', 'N/A')}")
        else:
            print("✗ Login form not found")
    else:
        print(f"✗ Login page failed to load: {response.status_code}")
    
    # Test 3: Test admin login
    print("\n3. Testing admin login...")
    login_data = {
        'username': 'admin',
        'password': 'admin123'  # Default password from build system
    }
    
    response = requests.post(f"{base_url}/login", data=login_data, allow_redirects=False)
    print(f"Login Status Code: {response.status_code}")
    
    if response.status_code == 302:  # Redirect after successful login
        print("✓ Admin login successful - redirected")
        redirect_url = response.headers.get('Location', '')
        print(f"Redirected to: {redirect_url}")
        
        # Test 4: Check if we can access the dashboard after login
        print("\n4. Testing dashboard access...")
        session = requests.Session()
        session.post(f"{base_url}/login", data=login_data)
        
        dashboard_response = session.get(f"{base_url}/")
        print(f"Dashboard Status Code: {dashboard_response.status_code}")
        
        if dashboard_response.status_code == 200:
            soup = BeautifulSoup(dashboard_response.text, 'html.parser')
            title = soup.find('title')
            if title:
                print(f"✓ Dashboard loaded: {title.text}")
            else:
                print("✓ Dashboard loaded (no title found)")
        else:
            print(f"✗ Dashboard access failed: {dashboard_response.status_code}")
    else:
        print("✗ Admin login failed")
        print(f"Response: {response.text[:200]}...")
    
    print("\n" + "=" * 50)
    print("Login test completed!")

if __name__ == "__main__":
    test_login() 