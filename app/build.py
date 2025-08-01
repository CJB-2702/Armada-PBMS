#!/usr/bin/env python3
"""
Main build orchestrator for the Asset Management System
Coordinates the building of all database components in the correct order
"""

from app.models.build import build_all_models
from app import create_app

def build_database():
    """Main database build entry point"""
    print("=== Asset Management Database Builder ===")
    print("Phase 1A: Core Foundation Tables")
    print("Phase 1B: Core System Initialization")
    print("Phase 2: Asset Detail Tables") 
    print("Phase 3: Maintenance & Operations")
    print("Phase 4: Advanced Features")
    print("")
    
    # Create app context for the build process
    app = create_app()
    
    with app.app_context():
        try:
            success = build_all_models()
            
            if success:
                print("✓ Database build completed successfully")
                print("✓ All phases completed without errors")
                print("✓ System ready for use")
            else:
                print("✗ Database build failed")
                raise Exception("Database build failed")
                
        except Exception as e:
            print(f"✗ Build process failed with error: {str(e)}")
            raise

if __name__ == '__main__':
    # This can be run directly for testing
    build_database() 