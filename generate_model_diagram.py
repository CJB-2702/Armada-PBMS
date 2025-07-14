#!/usr/bin/env python3
"""
Model Diagram Generator for Armada PBMS
Scans all model files and generates a comprehensive diagram of tables, relationships, and columns.
"""

import os
import sys
import inspect
from pathlib import Path
from collections import defaultdict

# Add the app directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

def get_model_info():
    """Scan all model files and extract table information without database access"""
    
    # Import the models directly
    try:
        from app.models.BaseModels.Users import User
        from app.models.BaseModels.Asset import AssetTypes, Asset
        from app.models.BaseModels.Locations import MajorLocation, MinorLocation
        from app.models.BaseModels.Event import Event, EventTypes
        from app.models.BaseModels.ProtoClasses import UserCreated, Types
    except ImportError as e:
        print(f"Error importing models: {e}")
        return {}
    
    # Get all SQLAlchemy models
    models = {}
    
    # Collect all model classes
    model_classes = [
        User, AssetTypes, Asset, MajorLocation, MinorLocation, Event, EventTypes,
        UserCreated, Types
    ]
    
    for model_class in model_classes:
        # Skip if no table name (abstract classes)
        if not hasattr(model_class, '__tablename__') or not model_class.__tablename__:
            continue
            
        table_name = model_class.__tablename__
        models[table_name] = {
            'class_name': model_class.__name__,
            'is_abstract': getattr(model_class, '__abstract__', False),
            'parent_classes': [cls.__name__ for cls in model_class.__mro__[1:] if hasattr(cls, '__name__')],
            'columns': [],
            'foreign_keys': [],
            'relationships': []
        }
        
        # Extract column information from the model's __table__ attribute
        if hasattr(model_class, '__table__'):
            for column_name, column in model_class.__table__.columns.items():
                column_info = {
                    'name': column_name,
                    'type': str(column.type),
                    'nullable': column.nullable,
                    'primary_key': column.primary_key,
                    'unique': column.unique,
                    'default': str(column.default) if column.default else None,
                    'foreign_key': None
                }
                
                # Check for foreign key
                if column.foreign_keys:
                    for fk in column.foreign_keys:
                        column_info['foreign_key'] = f"{fk.column.table.name}.{fk.column.name}"
                        models[table_name]['foreign_keys'].append({
                            'column': column_name,
                            'references': f"{fk.column.table.name}.{fk.column.name}"
                        })
                
                models[table_name]['columns'].append(column_info)
        
        # Extract relationship information
        if hasattr(model_class, '__mapper__'):
            for rel_name, relationship in model_class.__mapper__.relationships.items():
                models[table_name]['relationships'].append({
                    'name': rel_name,
                    'target': relationship.mapper.class_.__name__,
                    'type': str(relationship.direction),
                    'backref': relationship.backref
                })
    
    return models

def generate_text_diagram(models):
    """Generate a text-based diagram from the model information"""
    
    lines = []
    lines.append("=" * 80)
    lines.append("ARMADA PBMS - DATABASE MODEL DIAGRAM")
    lines.append("=" * 80)
    lines.append("")
    
    # Group tables by inheritance
    abstract_tables = {}
    concrete_tables = {}
    
    for table_name, table_info in models.items():
        if table_info['is_abstract']:
            abstract_tables[table_name] = table_info
        else:
            concrete_tables[table_name] = table_info
    
    # Display abstract base classes
    if abstract_tables:
        lines.append("ABSTRACT BASE CLASSES:")
        lines.append("-" * 40)
        for table_name, table_info in abstract_tables.items():
            lines.append(f"📋 {table_name} ({table_info['class_name']})")
            lines.append(f"   Parent Classes: {', '.join(table_info['parent_classes'])}")
            lines.append("")
    
    # Display concrete tables
    lines.append("CONCRETE TABLES:")
    lines.append("-" * 40)
    
    for table_name, table_info in concrete_tables.items():
        lines.append(f"🗃️  {table_name} ({table_info['class_name']})")
        
        # Show inheritance
        if table_info['parent_classes']:
            lines.append(f"   Inherits from: {', '.join(table_info['parent_classes'])}")
        
        # Show columns
        lines.append("   Columns:")
        for column in table_info['columns']:
            pk = " 🔑" if column['primary_key'] else ""
            fk = f" 🔗->{column['foreign_key']}" if column['foreign_key'] else ""
            unique = " 🔒" if column['unique'] else ""
            nullable = "" if column['nullable'] else " NOT NULL"
            
            lines.append(f"     • {column['name']}: {column['type']}{nullable}{pk}{unique}{fk}")
        
        # Show relationships
        if table_info['relationships']:
            lines.append("   Relationships:")
            for rel in table_info['relationships']:
                lines.append(f"     • {rel['name']} -> {rel['target']} ({rel['type']})")
        
        lines.append("")
    
    # Show foreign key relationships
    lines.append("FOREIGN KEY RELATIONSHIPS:")
    lines.append("-" * 40)
    
    for table_name, table_info in concrete_tables.items():
        for fk in table_info['foreign_keys']:
            referenced_table = fk['references'].split('.')[0]
            lines.append(f"   {table_name}.{fk['column']} -> {fk['references']}")
    
    lines.append("")
    lines.append("=" * 80)
    
    return "\n".join(lines)

def generate_mermaid_diagram(models):
    """Generate a Mermaid diagram from the model information"""
    
    mermaid_lines = [
        "```mermaid",
        "erDiagram",
        ""
    ]
    
    # Add table definitions
    for table_name, table_info in models.items():
        if table_info['is_abstract']:
            continue
            
        mermaid_lines.append(f"    {table_name} {{")
        
        # Add columns
        for column in table_info['columns']:
            column_type = column['type'].split('(')[0]  # Simplify type names
            nullable = "" if column['nullable'] else " NOT NULL"
            pk = " PK" if column['primary_key'] else ""
            unique = " UNIQUE" if column['unique'] else ""
            fk = f" FK->{column['foreign_key']}" if column['foreign_key'] else ""
            
            mermaid_lines.append(f"        {column_type} {column['name']}{nullable}{pk}{unique}{fk}")
        
        mermaid_lines.append("    }")
        mermaid_lines.append("")
    
    # Add relationships
    for table_name, table_info in models.items():
        if table_info['is_abstract']:
            continue
            
        for fk in table_info['foreign_keys']:
            referenced_table = fk['references'].split('.')[0]
            mermaid_lines.append(f"    {table_name} ||--o{{ {referenced_table} : \"{fk['column']}\"")
    
    mermaid_lines.append("```")
    
    return "\n".join(mermaid_lines)

def generate_markdown_table(models):
    """Generate a markdown table of all tables and columns"""
    
    lines = []
    lines.append("# Armada PBMS Database Schema")
    lines.append("")
    
    # Create table of contents
    lines.append("## Table of Contents")
    concrete_tables = [name for name, info in models.items() if not info['is_abstract']]
    for table_name in sorted(concrete_tables):
        lines.append(f"- [{table_name}](#{table_name.lower()})")
    lines.append("")
    
    # Generate detailed table information
    for table_name in sorted(concrete_tables):
        table_info = models[table_name]
        
        lines.append(f"## {table_name}")
        lines.append("")
        lines.append(f"**Class:** {table_info['class_name']}")
        
        if table_info['parent_classes']:
            lines.append(f"**Inherits from:** {', '.join(table_info['parent_classes'])}")
        
        lines.append("")
        lines.append("### Columns")
        lines.append("")
        lines.append("| Column | Type | Nullable | Primary Key | Unique | Foreign Key | Default |")
        lines.append("|--------|------|----------|-------------|--------|-------------|---------|")
        
        for column in table_info['columns']:
            nullable = "No" if not column['nullable'] else "Yes"
            pk = "Yes" if column['primary_key'] else "No"
            unique = "Yes" if column['unique'] else "No"
            fk = column['foreign_key'] if column['foreign_key'] else ""
            default = column['default'] if column['default'] else ""
            
            lines.append(f"| {column['name']} | {column['type']} | {nullable} | {pk} | {unique} | {fk} | {default} |")
        
        lines.append("")
        
        # Show relationships
        if table_info['relationships']:
            lines.append("### Relationships")
            lines.append("")
            for rel in table_info['relationships']:
                lines.append(f"- **{rel['name']}**: {rel['type']} relationship to `{rel['target']}`")
            lines.append("")
        
        lines.append("---")
        lines.append("")
    
    return "\n".join(lines)

def main():
    """Main function to generate all diagrams"""
    
    print("🔍 Scanning models...")
    models = get_model_info()
    
    if not models:
        print("❌ No models found or error occurred")
        return
    
    print(f"✅ Found {len(models)} model classes")
    
    # Generate different types of diagrams
    outputs = {
        'text_diagram.txt': generate_text_diagram(models),
        'mermaid_diagram.md': generate_mermaid_diagram(models),
        'schema_documentation.md': generate_markdown_table(models)
    }
    
    # Ensure output directory exists
    output_dir = os.path.join(os.path.dirname(__file__), 'MetaInfo', 'model')
    os.makedirs(output_dir, exist_ok=True)
    
    # Write output files
    for filename, content in outputs.items():
        output_path = os.path.join(output_dir, filename)
        with open(output_path, 'w') as f:
            f.write(content)
        print(f"📄 Generated {output_path}")
    
    # Also print the text diagram to console
    print("\n" + "="*80)
    print("CONSOLE OUTPUT:")
    print("="*80)
    print(outputs['text_diagram.txt'])

if __name__ == "__main__":
    main() 