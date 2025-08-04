#!/usr/bin/env python3
"""
Simple Hello World Flask app to test database creation and data insertion
"""

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import os

# Initialize Flask app
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///helloworld.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize SQLAlchemy
db = SQLAlchemy(app)

# Define a simple model
class TableCreated(db.Model):
    __tablename__ = 'tablecreated'
    
    id = db.Column(db.Integer, primary_key=True)
    yes = db.Column(db.Boolean, default=True)

def test_helloworld():
    """Test creating database, table, and inserting data"""
    print("=== Hello World Database Test ===")
    
    try:
        with app.app_context():
            # Step 1: Create all tables
            print("1. Creating database tables...")
            db.create_all()
            print("   ✓ Tables created successfully")
            
            # Step 2: Insert a row with boolean 'yes'
            print("2. Inserting data...")
            new_row = TableCreated(yes=True)
            db.session.add(new_row)
            db.session.commit()
            print("   ✓ Data inserted successfully")
            
            # Step 3: Verify table exists
            print("3. Verifying table exists...")
            inspector = db.inspect(db.engine)
            tables = inspector.get_table_names()
            
            if 'tablecreated' in tables:
                print("   ✓ Table 'tablecreated' exists")
            else:
                print("   ✗ Table 'tablecreated' missing")
                return False
            
            # Step 4: Verify data was inserted
            print("4. Verifying data was inserted...")
            result = TableCreated.query.first()
            if result and result.yes:
                print("   ✓ Row found with yes=True")
                print(f"   ✓ Row ID: {result.id}")
            else:
                print("   ✗ No row found or yes is not True")
                return False
            
            # Step 5: Show table schema
            print("5. Table schema:")
            columns = inspector.get_columns('tablecreated')
            for column in columns:
                nullable = "NULL" if column['nullable'] else "NOT NULL"
                print(f"   - {column['name']}: {column['type']} {nullable}")
            
            # Step 6: Count rows
            row_count = TableCreated.query.count()
            print(f"6. Total rows in table: {row_count}")
            
        print("\n=== Hello World Test PASSED ===")
        return True
        
    except Exception as e:
        print(f"\n=== Hello World Test FAILED ===")
        print(f"Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    success = test_helloworld()
    import sys
    sys.exit(0 if success else 1) 