#!/usr/bin/env python3
"""
Debug script to output all database tables, columns, and data to instance/debug.md
"""

from app.build_app import create_build_app, db
from sqlalchemy import inspect
import os

def debug_database():
    """Output all database information to debug.md"""
    app = create_build_app()
    
    with app.app_context():
        # Create tables if they don't exist
        db.create_all()
        inspector = inspect(db.engine)
        
        # Create debug.md content
        content = []
        content.append("# Database Debug Information")
        content.append("")
        content.append(f"Generated on: {__import__('datetime').datetime.now()}")
        content.append("")
        
        # Get all tables
        tables = inspector.get_table_names()
        content.append(f"## Tables ({len(tables)})")
        content.append("")
        
        for table_name in sorted(tables):
            content.append(f"### Table: `{table_name}`")
            content.append("")
            
            # Get columns
            columns = inspector.get_columns(table_name)
            content.append("#### Columns:")
            content.append("")
            content.append("| Column | Type | Nullable | Default | Primary Key |")
            content.append("|--------|------|----------|---------|-------------|")
            
            for column in columns:
                nullable = "YES" if column['nullable'] else "NO"
                default = str(column['default']) if column['default'] is not None else ""
                primary_key = "YES" if column.get('primary_key', False) else "NO"
                content.append(f"| {column['name']} | {column['type']} | {nullable} | {default} | {primary_key} |")
            
            content.append("")
            
            # Get foreign keys
            foreign_keys = inspector.get_foreign_keys(table_name)
            if foreign_keys:
                content.append("#### Foreign Keys:")
                content.append("")
                for fk in foreign_keys:
                    content.append(f"- `{fk['constrained_columns']}` → `{fk['referred_table']}.{fk['referred_columns']}`")
                content.append("")
            
            # Get indexes
            indexes = inspector.get_indexes(table_name)
            if indexes:
                content.append("#### Indexes:")
                content.append("")
                for index in indexes:
                    unique = "UNIQUE" if index['unique'] else "NON-UNIQUE"
                    content.append(f"- `{index['name']}` ({unique}): {index['column_names']}")
                content.append("")
            
            # Get row count and sample data
            try:
                result = db.session.execute(f"SELECT COUNT(*) as count FROM {table_name}")
                row_count = result.fetchone()[0]
                content.append(f"#### Row Count: {row_count}")
                content.append("")
                
                if row_count > 0:
                    content.append("#### Sample Data:")
                    content.append("")
                    
                    # Get sample rows (limit to 10)
                    sample_result = db.session.execute(f"SELECT * FROM {table_name} LIMIT 10")
                    rows = sample_result.fetchall()
                    column_names = [desc[0] for desc in sample_result.description]
                    
                    if rows:
                        # Create header
                        content.append("| " + " | ".join(column_names) + " |")
                        content.append("|" + "|".join(["---"] * len(column_names)) + "|")
                        
                        # Add data rows
                        for row in rows:
                            formatted_row = []
                            for value in row:
                                if value is None:
                                    formatted_row.append("NULL")
                                else:
                                    formatted_row.append(str(value))
                            content.append("| " + " | ".join(formatted_row) + " |")
                        
                        if row_count > 10:
                            content.append(f"")
                            content.append(f"*... and {row_count - 10} more rows*")
                    content.append("")
                else:
                    content.append("#### Data: *No rows*")
                    content.append("")
                    
            except Exception as e:
                content.append(f"#### Error reading data: {e}")
                content.append("")
            
            content.append("---")
            content.append("")
        
        # Write to file
        os.makedirs('instance', exist_ok=True)
        with open('instance/debug.md', 'w') as f:
            f.write('\n'.join(content))
        
        print(f"✓ Database debug information written to instance/debug.md")
        print(f"✓ Found {len(tables)} tables")
        for table in sorted(tables):
            try:
                result = db.session.execute(f"SELECT COUNT(*) as count FROM {table}")
                count = result.fetchone()[0]
                print(f"  - {table}: {count} rows")
            except:
                print(f"  - {table}: error reading count")

if __name__ == '__main__':
    debug_database() 