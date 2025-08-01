#!/usr/bin/env python3
"""
Run script for the Asset Management System
"""

from app import create_app
from app.build import build_database
import sys
import argparse

app = create_app()

def parse_arguments():
    """Parse command line arguments for build phases"""
    parser = argparse.ArgumentParser(description='Asset Management System')
    parser.add_argument('--phase1', action='store_true', 
                       help='Build only Phase 1 (Core Foundation Tables and System Initialization)')
    parser.add_argument('--phase2', action='store_true', 
                       help='Build Phase 1 and Phase 2 (Core + Asset Detail Tables)')
    parser.add_argument('--build-only', action='store_true',
                       help='Build database only, do not start the web server')
    
    return parser.parse_args()

if __name__ == '__main__':
    args = parse_arguments()
    
    print("Starting Asset Management System...")
    
    # Determine build phase based on arguments
    if args.phase1:
        print("=== Building Phase 1 Only ===")
        print("Phase 1A: Core Foundation Tables")
        print("Phase 1B: Core System Initialization")
        build_phase = 'phase1'
    elif args.phase2:
        print("=== Building Phase 1 and Phase 2 ===")
        print("Phase 1A: Core Foundation Tables")
        print("Phase 1B: Core System Initialization")
        print("Phase 2: Asset Detail Tables")
        build_phase = 'phase2'
    else:
        print("=== Building All Phases ===")
        print("Phase 1A: Core Foundation Tables")
        print("Phase 1B: Core System Initialization")
        print("Phase 2: Asset Detail Tables")
        print("Phase 3: Maintenance & Operations")
        print("Phase 4: Advanced Features")
        build_phase = 'all'
    print("")
    
    # Build database first
    build_database(build_phase=build_phase)
    
    if args.build_only:
        print("Build completed. Exiting without starting web server.")
        sys.exit(0)
    
    print("")
    print("Access the application at: http://localhost:5000")
    app.run(debug=True, host='0.0.0.0', port=5000) 