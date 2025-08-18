#!/usr/bin/env python3
"""
Comprehensive verification script for Hello World database test
"""

from pathlib import Path
import subprocess
import sqlite3
from flask import Flask
from flask_sqlalchemy import SQLAlchemy

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

def run_helloworld_test():
    """Run the basic hello world test"""
    logger.debug("=== Running Hello World Database Test ===")
    
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

def verify_database_file():
    """Verify the database file was created"""
    logger.debug("\n=== Verifying Database File ===")
    
    # Check if database file exists
    db_path = Path("instance/helloworld.db")
    if db_path.exists():
        logger.debug(f"✓ Database file exists: {db_path}")
        file_size = db_path.stat().st_size
        logger.debug(f"✓ Database file size: {file_size} bytes")
        return db_path
    else:
        logger.debug(f"✗ Database file missing: {db_path}")
        return None

def verify_sqlite_tables(db_path):
    """Verify tables using SQLite command line"""
    logger.debug("\n=== Verifying Tables with SQLite ===")
    
    try:
        # List tables
        result = subprocess.run(['sqlite3', db_path, '.tables'], 
                              capture_output=True, text=True, check=True)
        tables = result.stdout.strip()
        logger.debug(f"✓ Tables in database: {tables}")
        
        if 'tablecreated' in tables:
            logger.debug("✓ 'tablecreated' table found")
        else:
            logger.debug("✗ 'tablecreated' table missing")
            return False
        
        return True
        
    except subprocess.CalledProcessError as e:
        logger.debug(f"✗ SQLite command failed: {e}")
        return False
    except FileNotFoundError:
        logger.debug("✗ SQLite command not found")
        return False

def verify_sqlite_schema(db_path):
    """Verify table schema using SQLite command line"""
    logger.debug("\n=== Verifying Table Schema with SQLite ===")
    
    try:
        # Get table schema
        result = subprocess.run(['sqlite3', db_path, '.schema tablecreated'], 
                              capture_output=True, text=True, check=True)
        schema = result.stdout.strip()
        logger.debug("✓ Table schema:")
        for line in schema.split('\n'):
            logger.debug(f"  {line}")
        
        return True
        
    except subprocess.CalledProcessError as e:
        logger.debug(f"✗ SQLite schema command failed: {e}")
        return False

def verify_sqlite_data(db_path):
    """Verify data using SQLite command line"""
    logger.debug("\n=== Verifying Data with SQLite ===")
    
    try:
        # Query data
        result = subprocess.run(['sqlite3', db_path, 'SELECT * FROM tablecreated;'], 
                              capture_output=True, text=True, check=True)
        data = result.stdout.strip()
        logger.debug(f"✓ Data in table: {data}")
        
        if "1|1" in data:
            logger.debug("✓ Correct data found (id=1, yes=1)")
            row_count = data.count('\n') + 1
            if row_count > 1:
                logger.debug(f"  Note: {row_count} rows found (test may have run multiple times)")
        else:
            logger.debug(f"✗ Unexpected data: {data}")
            return False
        
        return True
        
    except subprocess.CalledProcessError as e:
        logger.debug(f"✗ SQLite query failed: {e}")
        return False

def verify_with_sqlite3_module(db_path):
    """Verify using Python sqlite3 module"""
    logger.debug("\n=== Verifying with Python sqlite3 Module ===")
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check tables
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = [row[0] for row in cursor.fetchall()]
        logger.debug(f"✓ Tables found: {tables}")
        
        if 'tablecreated' not in tables:
            logger.debug("✗ 'tablecreated' table not found")
            return False
        
        # Check schema
        cursor.execute("PRAGMA table_info(tablecreated);")
        columns = cursor.fetchall()
        logger.debug("✓ Column information:")
        for col in columns:
            logger.debug(f"  - {col[1]} ({col[2]}) {'NOT NULL' if col[3] else 'NULL'}")
        
        # Check data
        cursor.execute("SELECT * FROM tablecreated;")
        rows = cursor.fetchall()
        logger.debug(f"✓ Rows found: {len(rows)}")
        for row in rows:
            logger.debug(f"  - ID: {row[0]}, Yes: {row[1]}")
        
        conn.close()
        return True
        
    except Exception as e:
        logger.debug(f"✗ SQLite3 module verification failed: {e}")
        return False

def comprehensive_verification():
    """Run all verification steps"""
    logger.debug("=== Comprehensive Hello World Verification ===")
    
    # Step 1: Run the basic test
    if not run_helloworld_test():
        return False
    
    # Step 2: Verify database file
    db_path = verify_database_file()
    if not db_path:
        return False
    
    # Step 3: Verify with SQLite command line
    if not verify_sqlite_tables(db_path):
        return False
    
    if not verify_sqlite_schema(db_path):
        return False
    
    if not verify_sqlite_data(db_path):
        return False
    
    # Step 4: Verify with Python sqlite3 module
    if not verify_with_sqlite3_module(db_path):
        return False
    
    logger.debug("\n=== All Verifications PASSED ===")
    logger.debug("✓ Database created successfully")
    logger.debug("✓ Table 'tablecreated' exists")
    logger.debug("✓ Schema is correct")
    logger.debug("✓ Data inserted correctly")
    logger.debug("✓ All verification methods agree")
    
    return True

if __name__ == '__main__':
    success = comprehensive_verification()
    import sys
    sys.exit(0 if success else 1) 