#!/usr/bin/env python3
"""
Test script to verify table creation for Phase 1 models
"""

import os
import sys
from flask import Flask
from flask_sqlalchemy import SQLAlchemy

# Create a minimal Flask app for testing
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///instance/test_asset_management.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize SQLAlchemy
db = SQLAlchemy(app)

def test_table_creation():
    """Test creating all tables without inserting data"""
    print("=== Testing Table Creation ===")
    
    try:
        # Import all models
        print("1. Importing models...")
        
        # Import User model first (independent)
        from app.models.core.user import User
        print("   ✓ User model imported")
        
        # Import UserCreatedBase
        from app.models.core.user_created_base import UserCreatedBase
        print("   ✓ UserCreatedBase imported")
        
        # Import models that inherit from UserCreatedBase
        from app.models.core.major_location import MajorLocation
        print("   ✓ MajorLocation model imported")
        
        from app.models.core.asset_type import AssetType
        print("   ✓ AssetType model imported")
        
        from app.models.core.make_model import MakeModel
        print("   ✓ MakeModel model imported")
        
        from app.models.core.asset import Asset
        print("   ✓ Asset model imported")
        
        from app.models.core.event import Event
        print("   ✓ Event model imported")
        
        # Create all tables
        print("\n2. Creating database tables...")
        with app.app_context():
            db.create_all()
            print("   ✓ All tables created successfully")
        
        # Verify tables exist
        print("\n3. Verifying tables exist...")
        with app.app_context():
            inspector = db.inspect(db.engine)
            tables = inspector.get_table_names()
            
            expected_tables = ['users', 'major_locations', 'asset_types', 'make_models', 'assets', 'events']
            
            for table in expected_tables:
                if table in tables:
                    print(f"   ✓ Table '{table}' exists")
                else:
                    print(f"   ✗ Table '{table}' missing")
                    return False
            
            print(f"   ✓ All {len(expected_tables)} expected tables found")
        
        # Show table schemas
        print("\n4. Table schemas:")
        with app.app_context():
            inspector = db.inspect(db.engine)
            for table_name in expected_tables:
                print(f"\n   Table: {table_name}")
                columns = inspector.get_columns(table_name)
                for column in columns:
                    nullable = "NULL" if column['nullable'] else "NOT NULL"
                    print(f"     - {column['name']}: {column['type']} {nullable}")
        
        print("\n=== Table Creation Test PASSED ===")
        return True
        
    except Exception as e:
        print(f"\n=== Table Creation Test FAILED ===")
        print(f"Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    success = test_table_creation()
    sys.exit(0 if success else 1) 