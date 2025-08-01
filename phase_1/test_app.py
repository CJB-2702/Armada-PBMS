#!/usr/bin/env python3
"""
Test Flask app that only creates tables without inserting data
"""

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
import os

# Initialize extensions
db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()

def create_test_app():
    app = Flask(__name__)
    
    # Configuration
    app.config['SECRET_KEY'] = 'test-secret-key'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test_asset_management.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    # Initialize extensions with app
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    
    # Import models to ensure they're registered
    from app.models.core.user import User
    from app.models.core.user_created_base import UserCreatedBase
    from app.models.core.major_location import MajorLocation
    from app.models.core.asset_type import AssetType
    from app.models.core.make_model import MakeModel
    from app.models.core.asset import Asset
    from app.models.core.event import Event
    
    return app

def test_table_creation():
    """Test creating all tables without inserting data"""
    print("=== Testing Table Creation ===")
    
    try:
        # Create the test app
        app = create_test_app()
        print("1. Test Flask app created successfully")
        
        # Test table creation
        with app.app_context():
            print("2. Creating database tables...")
            db.create_all()
            print("   ✓ All tables created successfully")
            
            # Verify tables exist
            print("3. Verifying tables exist...")
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
    import sys
    sys.exit(0 if success else 1) 