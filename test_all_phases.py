#!/usr/bin/env python3
"""
Comprehensive test script for all phases
Tests Phase 1, Phase 2, and Phase 3 in sequence
Deletes database between each phase to ensure clean testing
"""

import sys
import shutil
from pathlib import Path

def delete_database():
    """Delete the database file and instance directory"""
    print("🗑️  Deleting database...")
    
    # Remove database file
    db_file = Path("asset_management.db")
    if db_file.exists():
        db_file.unlink()
        print(f"   ✓ Removed {db_file}")
    
    # Remove instance directory
    instance_dir = Path("instance")
    if instance_dir.exists():
        shutil.rmtree(instance_dir)
        print(f"   ✓ Removed {instance_dir}/")
    
    # Remove phase-specific instance directories
    for phase in ["phase_1", "phase_2", "phase_3"]:
        phase_instance = Path(phase) / "instance"
        if phase_instance.exists():
            shutil.rmtree(phase_instance)
            print(f"   ✓ Removed {phase_instance}/")
    
    print("   ✓ Database cleanup complete\n")

def test_phase1():
    """Test Phase 1 implementation"""
    print("=" * 60)
    print("🧪 TESTING PHASE 1")
    print("=" * 60)
    
    try:
        # Import and run Phase 1 test
        sys.path.insert(0, str(Path(__file__).parent))
        from phase_1.test_phase1 import test_phase1_implementation
        
        success = test_phase1_implementation()
        if success:
            print("\n✅ PHASE 1 TEST PASSED")
            return True
        else:
            print("\n❌ PHASE 1 TEST FAILED")
            return False
            
    except Exception as e:
        print(f"\n❌ PHASE 1 TEST ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def test_phase2():
    """Test Phase 2 implementation"""
    print("=" * 60)
    print("🧪 TESTING PHASE 2")
    print("=" * 60)
    
    try:
        # Import and run Phase 2 test
        sys.path.insert(0, str(Path(__file__).parent))
        from phase_2.test_phase2 import test_phase2_functionality
        
        success = test_phase2_functionality()
        if success:
            print("\n✅ PHASE 2 TEST PASSED")
            return True
        else:
            print("\n❌ PHASE 2 TEST FAILED")
            return False
            
    except Exception as e:
        print(f"\n❌ PHASE 2 TEST ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def test_phase3():
    """Test Phase 3 implementation"""
    print("=" * 60)
    print("🧪 TESTING PHASE 3")
    print("=" * 60)
    
    try:
        # Import and run Phase 3 test
        sys.path.insert(0, str(Path(__file__).parent))
        from test_phase3 import test_phase3_functionality
        
        test_phase3_functionality()
        print("\n✅ PHASE 3 TEST PASSED")
        return True
            
    except Exception as e:
        print(f"\n❌ PHASE 3 TEST ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def run_all_tests():
    """Run all phase tests in sequence"""
    print("🚀 STARTING COMPREHENSIVE PHASE TESTING")
    print("=" * 60)
    print("This will test all phases using centralized build_data.json")
    print("Database will be deleted between each phase for clean testing")
    print("=" * 60)
    
    # Test Phase 1
    delete_database()
    if not test_phase1():
        print("\n❌ STOPPING: Phase 1 failed")
        return False
    
    # Test Phase 2
    delete_database()
    if not test_phase2():
        print("\n❌ STOPPING: Phase 2 failed")
        return False
    
    # Test Phase 3
    delete_database()
    if not test_phase3():
        print("\n❌ STOPPING: Phase 3 failed")
        return False
    
    # Final cleanup
    delete_database()
    
    print("\n" + "=" * 60)
    print("🎉 ALL PHASES TESTED SUCCESSFULLY!")
    print("=" * 60)
    print("✅ Phase 1: Core models and data initialization")
    print("✅ Phase 2: Asset detail table system")
    print("✅ Phase 3: Automatic detail creation")
    print("\nAll phases now use centralized build_data.json from app/utils/")
    print("Data consistency verified across all phases")
    
    return True

if __name__ == '__main__':
    success = run_all_tests()
    sys.exit(0 if success else 1) 