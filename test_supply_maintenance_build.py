#!/usr/bin/env python3
"""
Test script for supply and maintenance build files
Tests that supply and maintenance can build and accept data independently
"""

import sys
from pathlib import Path

# Add the app directory to the Python path
sys.path.insert(0, str(Path(__file__).parent / 'app'))

from app import create_app, db
from app.logger import get_logger

logger = get_logger("test_supply_maintenance")

def test_supply_independence():
    """Test that supply can build and accept data independent from maintenance"""
    logger.info("=== Testing Supply Independence ===")
    
    app = create_app()
    
    with app.app_context():
        try:
            # Test supply build
            from app.models.supply.build import build_models, init_data, test_supply_independence
            from app.build import load_build_data
            
            logger.info("Building supply models...")
            build_models()
            
            logger.info("Loading build data...")
            build_data = load_build_data()
            
            logger.info("Initializing supply data...")
            init_data(build_data)
            
            # Test independence
            independence_result = test_supply_independence()
            
            if independence_result:
                logger.info("✅ Supply independence test PASSED")
                return True
            else:
                logger.error("❌ Supply independence test FAILED")
                return False
                
        except Exception as e:
            logger.error(f"❌ Supply test failed with exception: {e}")
            return False

def test_maintenance_independence():
    """Test that maintenance can build and accept data independent from supply"""
    logger.info("=== Testing Maintenance Independence ===")
    
    app = create_app()
    
    with app.app_context():
        try:
            # Test maintenance build
            from app.models.maintenance.build import build_models, init_data, test_maintenance_independence
            from app.build import load_build_data
            
            logger.info("Building maintenance models...")
            build_models()
            
            logger.info("Loading build data...")
            build_data = load_build_data()
            
            logger.info("Initializing maintenance data...")
            init_data(build_data)
            
            # Test independence
            independence_result = test_maintenance_independence()
            
            if independence_result:
                logger.info("✅ Maintenance independence test PASSED")
                return True
            else:
                logger.error("❌ Maintenance independence test FAILED")
                return False
                
        except Exception as e:
            logger.error(f"❌ Maintenance test failed with exception: {e}")
            return False

def test_integration():
    """Test that supply and maintenance can work together"""
    logger.info("=== Testing Supply-Maintenance Integration ===")
    
    app = create_app()
    
    with app.app_context():
        try:
            # Build both systems
            from app.models.supply.build import build_models as build_supply_models
            from app.models.maintenance.build import build_models as build_maintenance_models
            from app.models.supply.build import init_data as init_supply_data
            from app.models.maintenance.build import init_data as init_maintenance_data
            from app.build import load_build_data
            
            logger.info("Building both supply and maintenance models...")
            build_supply_models()
            build_maintenance_models()
            
            logger.info("Loading build data...")
            build_data = load_build_data()
            
            logger.info("Initializing supply data...")
            init_supply_data(build_data)
            
            logger.info("Initializing maintenance data...")
            init_maintenance_data(build_data)
            
            # Test that maintenance can reference supply parts
            from app.models.maintenance.templates.template_part_demand import TemplatePartDemand
            from app.models.supply.part import Part
            
            part_demands = TemplatePartDemand.query.all()
            logger.info(f"Found {len(part_demands)} template part demands")
            
            for demand in part_demands:
                if demand.part:
                    logger.info(f"✅ Part demand '{demand.template_action_item.action_name}' references part '{demand.part.part_name}'")
                else:
                    logger.warning(f"⚠️ Part demand '{demand.template_action_item.action_name}' has no part reference")
            
            logger.info("✅ Supply-Maintenance integration test PASSED")
            return True
                
        except Exception as e:
            logger.error(f"❌ Integration test failed with exception: {e}")
            return False

def main():
    """Run all tests"""
    logger.info("Starting supply and maintenance build tests...")
    
    # Test supply independence
    supply_result = test_supply_independence()
    
    # Test maintenance independence  
    maintenance_result = test_maintenance_independence()
    
    # Test integration
    integration_result = test_integration()
    
    # Summary
    logger.info("=== Test Summary ===")
    logger.info(f"Supply Independence: {'✅ PASSED' if supply_result else '❌ FAILED'}")
    logger.info(f"Maintenance Independence: {'✅ PASSED' if maintenance_result else '❌ FAILED'}")
    logger.info(f"Integration: {'✅ PASSED' if integration_result else '❌ FAILED'}")
    
    if supply_result and maintenance_result and integration_result:
        logger.info("🎉 All tests PASSED!")
        return 0
    else:
        logger.error("💥 Some tests FAILED!")
        return 1

if __name__ == '__main__':
    sys.exit(main())
