#!/usr/bin/env python3
"""
Main build orchestrator for the Asset Management System
Coordinates the building of all database components in the correct order
"""

from app.models.build import build_all_models, insert_all_data
from app import create_app

def build_database(build_phase='all', data_phase='all'):
    """
    Main database build entry point
    
    Args:
        build_phase (str): Build phase to execute
            - 'phase1': Core Foundation Tables only
            - 'phase2': Phase 1 + Asset Detail Tables
            - 'phase3': Phase 1 + Phase 2 + Automatic Detail Insertion
            - 'all': All phases (default = phase3)
        data_phase (str): Data insertion phase to execute
            - 'phase1': Core System Initialization only
            - 'phase2': Phase 1 + Asset Detail Data (manual insertion)
            - 'phase3': Phase 1 + Update auto-generated details
            - 'all': highest phase (default = phase3)
            - 'none': Skip data insertion
    """
    print("=== Asset Management Database Builder ===")
    print("Phase 1A: Core Foundation Tables (Models)")
    print("Phase 1B: Core System Initialization (Data)")
    print("Phase 2A: Asset Detail Tables (Models)")
    print("Phase 2B: Asset Detail Data (Data)")
    print("Phase 3A: Automatic Detail Insertion (Models)")
    print("Phase 3B: Update Auto-Generated Details (Data)")
    print("")
    
    # Determine what to build
    if build_phase == 'phase1':
        print("=== Building Phase 1 Models Only ===")
    elif build_phase == 'phase2':
        print("=== Building Phase 1 and Phase 2 Models ===")
    elif build_phase == 'phase3':
        print("=== Building Phase 1, Phase 2, and Phase 3 Models ===")
    else:
        print("=== Building All Phase Models (Phase 3) ===")
    
    # Determine what data to insert
    if data_phase == 'none':
        print("=== Skipping Data Insertion ===")
    elif data_phase == 'phase1':
        print("=== Inserting Phase 1 Data Only ===")
    elif data_phase == 'phase2':
        print("=== Inserting Phase 1 and Phase 2 Data ===")
    elif data_phase == 'phase3':
        print("=== Inserting Phase 1 and Phase 3 Data (Update auto-generated details) ===")
    else:
        print("=== Inserting All Phase Data (Phase 3) ===")
    print("")
    
    # Create app context for the build process
    app = create_app()
    
    with app.app_context():
        try:
            # Step 1: Build models
            print("=== Step 1: Building Models ===")
            success = build_all_models(build_phase=build_phase)
            
            if not success:
                print("✗ Model building failed")
                raise Exception("Model building failed")
            
            # Step 2: Insert data (if requested)
            if data_phase != 'none':
                print("\n=== Step 2: Inserting Data ===")
                success = insert_all_data(data_phase=data_phase)
                
                if not success:
                    print("✗ Data insertion failed")
                    raise Exception("Data insertion failed")
            
            # Success summary
            print("\n=== Build Summary ===")
            if build_phase == 'phase1':
                print("✓ Phase 1 models built successfully")
            elif build_phase == 'phase2':
                print("✓ Phase 1 and Phase 2 models built successfully")
            elif build_phase == 'phase3':
                print("✓ Phase 1, Phase 2, and Phase 3 models built successfully")
            else:
                print("✓ All phase models built successfully")
            
            if data_phase == 'none':
                print("✓ No data inserted (models only)")
            elif data_phase == 'phase1':
                print("✓ Phase 1 data inserted successfully")
            elif data_phase == 'phase2':
                print("✓ Phase 1 and Phase 2 data inserted successfully")
            elif data_phase == 'phase3':
                print("✓ Phase 1 and Phase 3 data inserted successfully (auto-generated details updated)")
            else:
                print("✓ All phase data inserted successfully")
            
            print("✓ System ready for use")
            
        except Exception as e:
            print(f"✗ Build process failed with error: {str(e)}")
            raise

def build_models_only(build_phase='all'):
    """Build models only, no data insertion"""
    build_database(build_phase=build_phase, data_phase='none')

def insert_data_only(data_phase='all'):
    """Insert data only, assuming models already exist"""
    build_database(build_phase='none', data_phase=data_phase)

if __name__ == '__main__':
    # This can be run directly for testing
    build_database() 