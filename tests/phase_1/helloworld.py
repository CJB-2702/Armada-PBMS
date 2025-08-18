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
    logger.debug("=== Hello World Database Test ===")
    
    try:
        with app.app_context():
            # Step 1: Create all tables
            logger.debug("1. Creating database tables...")
            db.create_all()
            logger.debug("   ✓ Tables created successfully")
            
            # Step 2: Insert a row with boolean 'yes'
            logger.debug("2. Inserting data...")
            new_row = TableCreated(yes=True)
            db.session.add(new_row)
            db.session.commit()
            logger.debug("   ✓ Data inserted successfully")
            
            # Step 3: Verify table exists
            logger.debug("3. Verifying table exists...")
            inspector = db.inspect(db.engine)
            tables = inspector.get_table_names()
            
            if 'tablecreated' in tables:
                logger.debug("   ✓ Table 'tablecreated' exists")
            else:
                logger.debug("   ✗ Table 'tablecreated' missing")
                return False
            
            # Step 4: Verify data was inserted
            logger.debug("4. Verifying data was inserted...")
            result = TableCreated.query.first()
            if result and result.yes:
                logger.debug("   ✓ Row found with yes=True")
                logger.debug(f"   ✓ Row ID: {result.id}")
            else:
                logger.debug("   ✗ No row found or yes is not True")
                return False
            
            # Step 5: Show table schema
            logger.debug("5. Table schema:")
            columns = inspector.get_columns('tablecreated')
            for column in columns:
                nullable = "NULL" if column['nullable'] else "NOT NULL"
                logger.debug(f"   - {column['name']}: {column['type']} {nullable}")
            
            # Step 6: Count rows
            row_count = TableCreated.query.count()
            logger.debug(f"6. Total rows in table: {row_count}")
            
        logger.debug("\n=== Hello World Test PASSED ===")
        return True
        
    except Exception as e:
        logger.debug(f"\n=== Hello World Test FAILED ===")
        logger.debug(f"Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    success = test_helloworld()
    import sys
    sys.exit(0 if success else 1) 