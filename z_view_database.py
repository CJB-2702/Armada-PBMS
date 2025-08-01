#!/usr/bin/env python3
"""
Database Viewer for Asset Management System
Opens the SQLite database and displays all tables and their data
"""

import sqlite3
import os
from tabulate import tabulate

def get_database_path():
    """Get the path to the SQLite database file"""
    # Check if database exists in instance directory (Flask default)
    instance_path = os.path.join(os.getcwd(), 'instance', 'asset_management.db')
    if os.path.exists(instance_path):
        return instance_path
    
    # Check if database exists in current directory
    current_path = os.path.join(os.getcwd(), 'asset_management.db')
    if os.path.exists(current_path):
        return current_path
    
    raise FileNotFoundError("Database file not found. Please run the application first to create the database.")

def get_table_names(conn):
    """Get all table names from the database"""
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = [row[0] for row in cursor.fetchall()]
    return sorted(tables)

def get_table_schema(conn, table_name):
    """Get the schema for a specific table"""
    cursor = conn.cursor()
    cursor.execute(f"PRAGMA table_info({table_name});")
    columns = cursor.fetchall()
    return columns

def get_table_data(conn, table_name):
    """Get all data from a specific table"""
    cursor = conn.cursor()
    cursor.execute(f"SELECT * FROM {table_name};")
    rows = cursor.fetchall()
    
    # Get column names
    cursor.execute(f"PRAGMA table_info({table_name});")
    columns = [col[1] for col in cursor.fetchall()]
    
    return columns, rows

def format_data_for_display(columns, rows):
    """Format data for nice display"""
    if not rows:
        return []
    
    # Convert all data to strings for display
    formatted_rows = []
    for row in rows:
        formatted_row = []
        for value in row:
            if value is None:
                formatted_row.append("NULL")
            elif isinstance(value, bool):
                formatted_row.append("True" if value else "False")
            else:
                formatted_row.append(str(value))
        formatted_rows.append(formatted_row)
    
    return formatted_rows

def display_table_info(conn, table_name):
    """Display detailed information about a table"""
    print(f"\n{'='*80}")
    print(f"TABLE: {table_name.upper()}")
    print(f"{'='*80}")
    
    # Get and display schema
    schema = get_table_schema(conn, table_name)
    print(f"\nSCHEMA:")
    print(f"{'Column Name':<20} {'Type':<15} {'Nullable':<10} {'Primary Key':<12} {'Default'}")
    print("-" * 80)
    for col in schema:
        cid, name, type_name, not_null, default_val, pk = col
        nullable = "NO" if not_null else "YES"
        primary_key = "YES" if pk else "NO"
        default_str = str(default_val) if default_val is not None else "NULL"
        print(f"{name:<20} {type_name:<15} {nullable:<10} {primary_key:<12} {default_str}")
    
    # Get and display data
    try:
        columns, rows = get_table_data(conn, table_name)
        formatted_rows = format_data_for_display(columns, rows)
        
        print(f"\nDATA ({len(rows)} rows):")
        if formatted_rows:
            print(tabulate(formatted_rows, headers=columns, tablefmt="grid"))
        else:
            print("(No data)")
            
    except sqlite3.Error as e:
        print(f"Error reading data from {table_name}: {e}")

def main():
    """Main function to display database contents"""
    print("Asset Management System - Database Viewer")
    print("=" * 50)
    
    try:
        # Get database path
        db_path = get_database_path()
        print(f"Database: {db_path}")
        
        # Connect to database
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row  # Enable row factory for better access
        
        # Get all table names
        tables = get_table_names(conn)
        print(f"\nFound {len(tables)} tables: {', '.join(tables)}")
        
        # Display information for each table
        for table_name in tables:
            display_table_info(conn, table_name)
        
        # Display summary
        print(f"\n{'='*80}")
        print("DATABASE SUMMARY")
        print(f"{'='*80}")
        
        total_rows = 0
        for table_name in tables:
            cursor = conn.cursor()
            cursor.execute(f"SELECT COUNT(*) FROM {table_name};")
            count = cursor.fetchone()[0]
            total_rows += count
            print(f"{table_name:<20}: {count:>5} rows")
        
        print(f"{'TOTAL':<20}: {total_rows:>5} rows")
        
        conn.close()
        print(f"\nDatabase connection closed.")
        
    except FileNotFoundError as e:
        print(f"Error: {e}")
        print("Please run 'python app.py' first to create the database.")
    except sqlite3.Error as e:
        print(f"Database error: {e}")
    except Exception as e:
        print(f"Unexpected error: {e}")

if __name__ == "__main__":
    main() 