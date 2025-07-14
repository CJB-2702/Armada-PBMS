#!/usr/bin/env python3
"""
Test script to verify database initialization order
"""

import sys
import os

# Add the app directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

from app import create_app
from app.utils.logger import get_logger

def test_initialization():
    """Test the database initialization process"""
    logger = get_logger()
    
    try:
        logger.info("=== Starting database initialization test ===")
        
        # Create the app (this will trigger the controlled initialization)
        app = create_app()
        
        logger.info("=== Database initialization test completed successfully ===")
        return True
        
    except Exception as e:
        logger.error(f"=== Database initialization test FAILED: {e} ===")
        return False

if __name__ == "__main__":
    success = test_initialization()
    sys.exit(0 if success else 1) 