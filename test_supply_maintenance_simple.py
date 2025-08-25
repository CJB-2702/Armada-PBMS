#!/usr/bin/env python3
"""
Simple test script for supply and maintenance build files
Builds the database first, then tests supply and maintenance independently
"""

import sys
from pathlib import Path

# Add the app directory to the Python path
sys.path.insert(0, str(Path(__file__).parent / 'app'))

from app import create_app, db
from app.logger import get_logger

logger = get_logger("test_supply_maintenance_simple")

def test_supply_build():
    """Test that supply can build and accept data"""
    logger.info("=== Testing Supply Build ===")
    
    app = create_app()
    
    with app.app_context():
        try:
            # Build all models first
            from app.build import build_models, insert_data
            
            logger.info("Building all models...")
            build_models('all')
            
            logger.info("Creating all tables...")
            db.create_all()
            
            logger.info("Inserting core data...")
            insert_data('phase1')
            
            logger.info("Inserting supply data...")
            insert_data('phase5')
            
            # Test that supply data was created
            from app.models.supply.part import Part
            from app.models.supply.tool import Tool
            from app.models.supply.part_demand import PartDemand
            
            parts_count = Part.query.count()
            tools_count = Tool.query.count()
            demands_count = PartDemand.query.count()
            
            logger.info(f"✅ Supply build test PASSED - Parts: {parts_count}, Tools: {tools_count}, Demands: {demands_count}")
            return True
                
        except Exception as e:
            logger.error(f"❌ Supply build test failed with exception: {e}")
            return False

def test_maintenance_build():
    """Test that maintenance can build and accept data"""
    logger.info("=== Testing Maintenance Build ===")
    
    app = create_app()
    
    with app.app_context():
        try:
            # Build all models first
            from app.build import build_models, insert_data
            
            logger.info("Building all models...")
            build_models('all')
            
            logger.info("Creating all tables...")
            db.create_all()
            
            logger.info("Inserting core data...")
            insert_data('phase1')
            
            logger.info("Inserting supply data...")
            insert_data('phase5')
            
            logger.info("Inserting maintenance data...")
            insert_data('phase4')
            
            # Test that maintenance data was created
            from app.models.maintenance.base.maintenance_plan import MaintenancePlan
            from app.models.maintenance.templates.template_action_set import TemplateActionSet
            from app.models.maintenance.templates.template_action_item import TemplateActionItem
            
            plans_count = MaintenancePlan.query.count()
            tas_count = TemplateActionSet.query.count()
            tai_count = TemplateActionItem.query.count()
            
            logger.info(f"✅ Maintenance build test PASSED - Plans: {plans_count}, Action Sets: {tas_count}, Action Items: {tai_count}")
            return True
                
        except Exception as e:
            logger.error(f"❌ Maintenance build test failed with exception: {e}")
            return False

def test_full_build():
    """Test the full build process with all phases"""
    logger.info("=== Testing Full Build Process ===")
    
    app = create_app()
    
    with app.app_context():
        try:
            from app.build import build_database
            
            logger.info("Running full build process...")
            build_database(build_phase='all', data_phase='all')
            
            # Test that all data was created
            from app.models.supply.part import Part
            from app.models.maintenance.base.maintenance_plan import MaintenancePlan
            
            parts_count = Part.query.count()
            plans_count = MaintenancePlan.query.count()
            
            logger.info(f"✅ Full build test PASSED - Parts: {parts_count}, Maintenance Plans: {plans_count}")
            return True
                
        except Exception as e:
            logger.error(f"❌ Full build test failed with exception: {e}")
            return False

def main():
    """Run all tests"""
    logger.info("Starting supply and maintenance build tests...")
    
    # Test supply build
    supply_result = test_supply_build()
    
    # Test maintenance build  
    maintenance_result = test_maintenance_build()
    
    # Test full build
    full_result = test_full_build()
    
    # Summary
    logger.info("=== Test Summary ===")
    logger.info(f"Supply Build: {'✅ PASSED' if supply_result else '❌ FAILED'}")
    logger.info(f"Maintenance Build: {'✅ PASSED' if maintenance_result else '❌ FAILED'}")
    logger.info(f"Full Build: {'✅ PASSED' if full_result else '❌ FAILED'}")
    
    if supply_result and maintenance_result and full_result:
        logger.info("🎉 All tests PASSED!")
        return 0
    else:
        logger.error("💥 Some tests FAILED!")
        return 1

if __name__ == '__main__':
    sys.exit(main())
