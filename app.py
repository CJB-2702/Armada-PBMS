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
    parser.add_argument('--phase3', action='store_true', 
                       help='Build Phase 1, Phase 2, and Phase 3 (Core + Asset Detail Tables + Automatic Detail Creation)')
    parser.add_argument('--phase4', action='store_true', 
                       help='Build Phase 1, Phase 2, Phase 3, and Phase 4 (Core + Asset Detail Tables + Automatic Detail Creation + User Interface)')
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
    elif args.phase3:
        print("=== Building Phase 1, Phase 2, and Phase 3 ===")
        print("Phase 1A: Core Foundation Tables")
        print("Phase 1B: Core System Initialization")
        print("Phase 2: Asset Detail Tables")
        print("Phase 3: Automatic Detail Creation")
        build_phase = 'phase3'
    elif args.phase4:
        print("=== Building Phase 1, Phase 2, Phase 3, and Phase 4 ===")
        print("Phase 1A: Core Foundation Tables")
        print("Phase 1B: Core System Initialization")
        print("Phase 2: Asset Detail Tables")
        print("Phase 3: Automatic Detail Creation")
        print("Phase 4: User Interface & Authentication")
        build_phase = 'phase4'
    else:
        print("=== Building All Phases ===")
        print("Phase 1A: Core Foundation Tables")
        print("Phase 1B: Core System Initialization")
        print("Phase 2: Asset Detail Tables")
        print("Phase 3: Automatic Detail Creation")
        print("Phase 4: User Interface & Authentication")
        build_phase = 'all'
    print("")
    
    # Build database first
    if args.phase1:
        build_database(build_phase=build_phase, data_phase='phase1')
    elif args.phase2:
        build_database(build_phase=build_phase, data_phase='phase2')
    elif args.phase3:
        build_database(build_phase=build_phase, data_phase='phase3')
    elif args.phase4:
        build_database(build_phase=build_phase, data_phase='phase4')
    else:
        build_database(build_phase=build_phase)
    
    if args.build_only:
        print("Build completed. Exiting without starting web server.")
        sys.exit(0)
    
    print("")
    print("Access the application at: http://localhost:5000")
    app.run(debug=True, host='127.0.0.1', port=5000) 