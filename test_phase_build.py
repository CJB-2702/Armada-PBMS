#!/usr/bin/env python3
"""
Test script to demonstrate the phase build functionality
"""

import sys
import os

# Add the current directory to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.build import build_database

def test_phase_builds():
    """Test different build phases"""
    
    print("=== Testing Phase Build Functionality ===\n")
    
    # Test Phase 1 only
    print("1. Testing Phase 1 build...")
    try:
        build_database(build_phase='phase1')
        print("✓ Phase 1 build test completed\n")
    except Exception as e:
        print(f"✗ Phase 1 build test failed: {e}\n")
    
    # Test Phase 2 (includes Phase 1)
    print("2. Testing Phase 2 build...")
    try:
        build_database(build_phase='phase2')
        print("✓ Phase 2 build test completed\n")
    except Exception as e:
        print(f"✗ Phase 2 build test failed: {e}\n")
    
    # Test All phases
    print("3. Testing All phases build...")
    try:
        build_database(build_phase='all')
        print("✓ All phases build test completed\n")
    except Exception as e:
        print(f"✗ All phases build test failed: {e}\n")

if __name__ == '__main__':
    test_phase_builds() 