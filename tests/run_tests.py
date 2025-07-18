#!/usr/bin/env python3
"""
Simple test runner for the Armada PBMS application
"""

import sys
import os
import pytest

# Add the parent directory to the Python path so we can import the app
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def main():
    """Run the tests"""
    print("Running Armada PBMS initialization tests...")
    print("=" * 50)
    
    # Run the tests with verbose output
    result = pytest.main([
        'test_app_initialization.py',
        '-v',
        '--tb=short'
    ])
    
    print("=" * 50)
    if result == 0:
        print("✅ All tests passed!")
    else:
        print("❌ Some tests failed!")
    
    return result

if __name__ == '__main__':
    sys.exit(main()) 