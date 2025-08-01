#!/usr/bin/env python3
"""
Run script for the Asset Management System
"""

from app import create_app
from app.build import build_database
import sys

app = create_app()

if __name__ == '__main__':
    print("Starting Asset Management System...")
    
    # Check for build phase arguments
    phase_1_only = '--phase1' in sys.argv
    phase_2_only = '--phase2' in sys.argv
    
    if phase_1_only:
        print("=== Building Phase 1 Only ===")
    elif phase_2_only:
        print("=== Building Phase 2 Only ===")
    else:
        print("Phase 1A: Core Foundation Tables")
        print("Phase 1B: Core System Initialization")
        print("Phase 2: Asset Detail Tables")
    print("")
    
    # Build database first
    build_database(phase_1_only=phase_1_only, phase_2_only=phase_2_only)
    
    print("")
    print("Access the application at: http://localhost:5000")
    app.run(debug=True, host='0.0.0.0', port=5000) 