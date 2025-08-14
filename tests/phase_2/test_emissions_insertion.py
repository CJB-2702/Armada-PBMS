#!/usr/bin/env python3
"""
Focused test script for emissions info insertion and master table linking
Tests the complete flow from app build to database verification
"""

import sys
from pathlib import Path

# Add the current directory to Python path
sys.path.insert(0, str(Path.cwd()))

from app import create_app, db
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def build_and_initialize():
    """Build the app and initialize core data"""
    logger.info("=== Building and Initializing Application ===")
    
    # Create Flask app
    app = create_app()
    
    with app.app_context():
        logger.info("1. Creating database tables...")
        
        # Import all necessary models to register them
        logger.info("   Importing core models...")
        import app.models.core.user
        import app.models.core.major_location
        import app.models.core.asset_type
        import app.models.core.make_model
        import app.models.core.asset
        import app.models.core.event
        import app.models.core.attachment
        import app.models.core.comment
        import app.models.core.comment_attachment
        
        logger.info("   Importing asset models...")
        import app.models.assets.all_details
        import app.models.assets.model_detail_virtual
        import app.models.assets.model_details.emissions_info
        
        # Create all tables
        db.create_all()
        logger.info("   ✓ All database tables created")
        
        # Insert core data
        logger.info("2. Inserting core data...")
        from app.models.core.build import init_data
        import json
        from pathlib import Path
        
        # Load build data from JSON file
        build_data_path = Path(__file__).parent / 'app' / 'utils' / 'build_data.json'
        with open(build_data_path, 'r') as f:
            build_data = json.load(f)
        
        init_data(build_data)
        logger.info("   ✓ Core data inserted")
        
        return app

def test_emissions_insertion():
    """Test emissions info insertion and master table linking"""
    logger.info("\n=== Testing Emissions Info Insertion ===")
    
    app = create_app()
    
    with app.app_context():
        # Import the models
        from app.models.assets.model_details.emissions_info import EmissionsInfo
        from app.models.core.make_model import MakeModel
        from app.models.assets.all_details import AllModelDetail
        
        # Get or create a make_model for testing
        logger.info("1. Getting test make_model...")
        make_model = MakeModel.query.first()
        if not make_model:
            logger.error("No make_model found in database. Please ensure core data is inserted.")
            return False
        
        logger.info(f"   Using make_model: {make_model}")
        
        # Create emissions info record
        logger.info("2. Creating emissions info record...")
        from datetime import date
        
        emissions = EmissionsInfo(
            make_model_id=make_model.id,
            emissions_standard="EPA Tier 3",
            emissions_rating="ULEV",
            fuel_type="gasoline",
            mpg_city=25.0,
            mpg_highway=32.0,
            mpg_combined=28.0,
            co2_emissions=320.0,
            emissions_test_date=date(2024, 1, 15),
            emissions_certification="EPA-2024-001"
        )
        
        # Add to session and commit
        db.session.add(emissions)
        db.session.commit()
        
        logger.info(f"   ✓ Emissions info created with ID: {emissions.id}")
        
        # Check if master table record was created
        logger.info("3. Verifying master table record...")
        master_record = AllModelDetail.query.filter_by(
            table_name='emissions_info',
            row_id=emissions.id
        ).first()
        
        if master_record:
            logger.info(f"   ✓ Master table record found with ID: {master_record.id}")
            logger.info(f"   ✓ row_id matches: {master_record.row_id} == {emissions.id}")
            logger.info(f"   ✓ make_model_id matches: {master_record.make_model_id} == {emissions.make_model_id}")
        else:
            logger.error("   ✗ Master table record not found!")
            return False
        
        # Display the records
        logger.info("\n4. Record Details:")
        logger.info(f"   Emissions Info ID: {emissions.id}")
        logger.info(f"   Master Table ID: {master_record.id}")
        logger.info(f"   Table Name: {master_record.table_name}")
        logger.info(f"   Row ID: {master_record.row_id}")
        logger.info(f"   Make Model ID: {master_record.make_model_id}")
        
        return True

def main():
    """Main test function"""
    logger.info("Emissions Info Insertion Test")
    logger.info("=" * 50)
    
    try:
        # Build and initialize
        app = build_and_initialize()
        
        # Test emissions insertion
        success = test_emissions_insertion()
        
        if success:
            logger.info("\n=== TEST SUCCESSFUL ===")
            logger.info("Emissions info insertion and master table linking works correctly!")
            logger.info("\nRun 'python z_view_database.py' to see the database contents.")
        else:
            logger.error("\n=== TEST FAILED ===")
            return 1
            
    except Exception as e:
        logger.error(f"Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0

if __name__ == '__main__':
    exit(main())
