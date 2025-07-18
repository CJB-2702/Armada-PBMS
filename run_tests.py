#!/usr/bin/env python3
"""
Test runner script for Armada PBMS
"""
import sys
import subprocess
import os

def run_tests(test_type=None):
    """Run tests with optional filtering"""
    cmd = ['python', '-m', 'pytest']
    
    if test_type:
        if test_type == 'unit':
            cmd.extend(['tests/unit/', '-m', 'unit'])
        elif test_type == 'integration':
            cmd.extend(['tests/integration/', '-m', 'integration'])
        elif test_type == 'functional':
            cmd.extend(['tests/functional/', '-m', 'functional'])
        else:
            print(f"Unknown test type: {test_type}")
            print("Available types: unit, integration, functional")
            return False
    else:
        # Run all tests
        cmd.append('tests/')
    
    print(f"Running tests: {' '.join(cmd)}")
    result = subprocess.run(cmd)
    return result.returncode == 0

def main():
    """Main function"""
    if len(sys.argv) > 1:
        test_type = sys.argv[1]
        success = run_tests(test_type)
    else:
        success = run_tests()
    
    if success:
        print("\n✅ All tests passed!")
        sys.exit(0)
    else:
        print("\n❌ Some tests failed!")
        sys.exit(1)

if __name__ == "__main__":
    main() 