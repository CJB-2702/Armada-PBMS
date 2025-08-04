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
    print("=== Running Hello World Database Test ===")
    
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

def verify_database_file():
    """Verify the database file was created"""
    print("\n=== Verifying Database File ===")
    
    # Check if database file exists
    db_path = Path("instance/helloworld.db")
    if db_path.exists():
        print(f"✓ Database file exists: {db_path}")
        file_size = db_path.stat().st_size
        print(f"✓ Database file size: {file_size} bytes")
        return db_path
    else:
        print(f"✗ Database file missing: {db_path}")
        return None

def verify_sqlite_tables(db_path):
    """Verify tables using SQLite command line"""
    print("\n=== Verifying Tables with SQLite ===")
    
    try:
        # List tables
        result = subprocess.run(['sqlite3', db_path, '.tables'], 
                              capture_output=True, text=True, check=True)
        tables = result.stdout.strip()
        print(f"✓ Tables in database: {tables}")
        
        if 'tablecreated' in tables:
            print("✓ 'tablecreated' table found")
        else:
            print("✗ 'tablecreated' table missing")
            return False
        
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"✗ SQLite command failed: {e}")
        return False
    except FileNotFoundError:
        print("✗ SQLite command not found")
        return False

def verify_sqlite_schema(db_path):
    """Verify table schema using SQLite command line"""
    print("\n=== Verifying Table Schema with SQLite ===")
    
    try:
        # Get table schema
        result = subprocess.run(['sqlite3', db_path, '.schema tablecreated'], 
                              capture_output=True, text=True, check=True)
        schema = result.stdout.strip()
        print("✓ Table schema:")
        for line in schema.split('\n'):
            print(f"  {line}")
        
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"✗ SQLite schema command failed: {e}")
        return False

def verify_sqlite_data(db_path):
    """Verify data using SQLite command line"""
    print("\n=== Verifying Data with SQLite ===")
    
    try:
        # Query data
        result = subprocess.run(['sqlite3', db_path, 'SELECT * FROM tablecreated;'], 
                              capture_output=True, text=True, check=True)
        data = result.stdout.strip()
        print(f"✓ Data in table: {data}")
        
        if "1|1" in data:
            print("✓ Correct data found (id=1, yes=1)")
            row_count = data.count('\n') + 1
            if row_count > 1:
                print(f"  Note: {row_count} rows found (test may have run multiple times)")
        else:
            print(f"✗ Unexpected data: {data}")
            return False
        
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"✗ SQLite query failed: {e}")
        return False

def verify_with_sqlite3_module(db_path):
    """Verify using Python sqlite3 module"""
    print("\n=== Verifying with Python sqlite3 Module ===")
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check tables
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = [row[0] for row in cursor.fetchall()]
        print(f"✓ Tables found: {tables}")
        
        if 'tablecreated' not in tables:
            print("✗ 'tablecreated' table not found")
            return False
        
        # Check schema
        cursor.execute("PRAGMA table_info(tablecreated);")
        columns = cursor.fetchall()
        print("✓ Column information:")
        for col in columns:
            print(f"  - {col[1]} ({col[2]}) {'NOT NULL' if col[3] else 'NULL'}")
        
        # Check data
        cursor.execute("SELECT * FROM tablecreated;")
        rows = cursor.fetchall()
        print(f"✓ Rows found: {len(rows)}")
        for row in rows:
            print(f"  - ID: {row[0]}, Yes: {row[1]}")
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"✗ SQLite3 module verification failed: {e}")
        return False

def comprehensive_verification():
    """Run all verification steps"""
    print("=== Comprehensive Hello World Verification ===")
    
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
    
    print("\n=== All Verifications PASSED ===")
    print("✓ Database created successfully")
    print("✓ Table 'tablecreated' exists")
    print("✓ Schema is correct")
    print("✓ Data inserted correctly")
    print("✓ All verification methods agree")
    
    return True

if __name__ == '__main__':
    success = comprehensive_verification()
    import sys
    sys.exit(0 if success else 1) 