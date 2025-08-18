#!/usr/bin/env python3
"""
Script to create master table tables in the database
"""

import sys
from pathlib import Path

# Add the app directory to the Python path
sys.path.insert(0, str(Path(__file__).parent))

from app import create_app, db

def create_master_tables():
    """Create the master table tables in the database"""
    app = create_app()
    
    with app.app_context():
        logger.debug("Creating master table tables...")
        
        # Import the master table models to register them
        from app.models.assets.all_details import AllAssetDetail, AllModelDetail
        
        try:
            # Create the tables
            db.create_all()
            logger.debug("✓ Successfully created all tables")
            
            # Verify the tables exist
            asset_count = AllAssetDetail.query.count()
            model_count = AllModelDetail.query.count()
            logger.debug(f"✓ Tables verified. Asset details: {asset_count}, Model details: {model_count}")
            
        except Exception as e:
            logger.debug(f"✗ Error creating tables: {e}")
            return
        
        logger.debug("✓ Master table creation completed!")

if __name__ == '__main__':
    create_master_tables()
