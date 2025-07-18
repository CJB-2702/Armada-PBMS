#!/usr/bin/env python3
"""
Database Schema Diagram Generator
Queries the SQLite database to extract all tables, columns, and foreign keys,
then generates a Mermaid ER diagram.
"""

import sqlite3
import sys
from pathlib import Path
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass


@dataclass
class Column:
    """Represents a database column"""
    name: str
    data_type: str
    not_null: bool
    default_value: Optional[str]
    primary_key: bool
    
    def format_type(self) -> str:
        """Format column type for Mermaid diagram"""
        col_type = self.data_type.upper()
        
        # Map SQLite types to more readable formats
        type_mapping = {
            'INTEGER': 'INT',
            'REAL': 'FLOAT',
            'TEXT': 'TEXT',
            'BLOB': 'BLOB',
            'BOOLEAN': 'BOOL',
            'DATETIME': 'DATETIME',
            'DATE': 'DATE'
        }
        
        return type_mapping.get(col_type, col_type)
    
    def get_constraints(self) -> List[str]:
        """Get formatted constraints for Mermaid diagram"""
        constraints = []
        
        if self.primary_key:
            constraints.append('PK')
        
        if self.not_null:
            constraints.append('NOT NULL')
        
        if self.default_value is not None:
            constraints.append(f"DEFAULT {self.default_value}")
        
        return constraints
    
    def to_mermaid_line(self) -> str:
        """Convert column to Mermaid diagram line"""
        col_type = self.format_type()
        constraints = self.get_constraints()
        constraint_str = " " + " ".join(constraints) if constraints else ""
        return f"        {col_type} {self.name}{constraint_str}"
    
    def to_summary_row(self) -> str:
        """Convert column to summary table row"""
        col_type = self.format_type()
        constraints = self.get_constraints()
        constraint_str = ", ".join(constraints) if constraints else ""
        return f"| {self.name} | {col_type} | {constraint_str} |"


@dataclass
class ForeignKey:
    """Represents a foreign key relationship"""
    from_column: str
    to_table: str
    to_column: str
    on_update: str
    on_delete: str
    
    def to_mermaid_relationship(self, from_table: str) -> str:
        """Convert foreign key to Mermaid relationship line"""
        # Determine relationship type based on column names and patterns
        if self.from_column.endswith('_id') or self.from_column.endswith('_UID'):
            # Many-to-one relationship
            return f"    {from_table} ||--o{{ {self.to_table} : \"{self.from_column} -> {self.to_column}\""
        else:
            # One-to-one relationship (less common)
            return f"    {from_table} ||--|| {self.to_table} : \"{self.from_column} -> {self.to_column}\""
    
    def to_summary_row(self) -> str:
        """Convert foreign key to summary table row"""
        return f"| {self.from_column} | {self.to_table}.{self.to_column} |"


@dataclass
class Index:
    """Represents a database index"""
    name: str
    unique: bool
    
    def to_summary_row(self) -> str:
        """Convert index to summary table row"""
        return f"| {self.name} | {'Yes' if self.unique else 'No'} |"


class Table:
    """Represents a database table"""
    
    def __init__(self, name: str):
        self.name = name
        self.columns: List[Column] = []
        self.foreign_keys: List[ForeignKey] = []
        self.indexes: List[Index] = []
    
    def add_column(self, column: Column):
        """Add a column to the table"""
        self.columns.append(column)
    
    def add_foreign_key(self, foreign_key: ForeignKey):
        """Add a foreign key to the table"""
        self.foreign_keys.append(foreign_key)
    
    def add_index(self, index: Index):
        """Add an index to the table"""
        self.indexes.append(index)
    
    def get_column_by_name(self, name: str) -> Optional[Column]:
        """Get a column by name"""
        for column in self.columns:
            if column.name == name:
                return column
        return None
    
    def is_foreign_key_column(self, column_name: str) -> bool:
        """Check if a column is a foreign key"""
        return any(fk.from_column == column_name for fk in self.foreign_keys)
    
    def should_include_in_relationship_diagram(self, column: Column) -> bool:
        """Check if column should be included in relationship diagram"""
        # Skip audit columns
        if column.name in ("updated_by", "created_by"):
            return False
        
        # Include primary keys and foreign keys
        return column.primary_key or self.is_foreign_key_column(column.name)
    
    def to_complete_mermaid(self) -> List[str]:
        """Convert table to complete Mermaid diagram lines"""
        lines = [f"    {self.name} {{"]
        for column in self.columns:
            lines.append(column.to_mermaid_line())
        lines.append("    }")
        return lines
    
    def to_relationship_mermaid(self) -> List[str]:
        """Convert table to relationship Mermaid diagram lines"""
        if not self.foreign_keys:
            return []
        
        lines = [f"    {self.name} {{"]
        for column in self.columns:
            if self.should_include_in_relationship_diagram(column):
                lines.append(column.to_mermaid_line())
        lines.append("    }")
        return lines
    
    def to_summary_section(self) -> List[str]:
        """Convert table to summary section"""
        lines = [
            f"## {self.name}",
            ""
        ]
        
        # Columns
        lines.extend([
            "### Columns",
            "| Column | Type | Constraints |",
            "|--------|------|-------------|"
        ])
        for column in self.columns:
            lines.append(column.to_summary_row())
        lines.append("")
        
        # Foreign Keys
        if self.foreign_keys:
            lines.extend([
                "### Foreign Keys",
                "| Column | References |",
                "|--------|------------|"
            ])
            for fk in self.foreign_keys:
                lines.append(fk.to_summary_row())
            lines.append("")
        
        # Indexes
        if self.indexes:
            lines.extend([
                "### Indexes",
                "| Name | Unique |",
                "|------|--------|"
            ])
            for idx in self.indexes:
                lines.append(idx.to_summary_row())
            lines.append("")
        
        lines.extend(["---", ""])
        return lines


class DatabaseSchema:
    """Manages database connection and schema extraction"""
    
    def __init__(self, db_path: Path):
        self.db_path = db_path
        self.tables: Dict[str, Table] = {}
    
    def connect(self) -> sqlite3.Connection:
        """Create a database connection"""
        return sqlite3.connect(self.db_path)
    
    def extract_schema(self):
        """Extract the complete database schema"""
        conn = self.connect()
        try:
            table_names = self._get_table_names(conn)
            
            for table_name in table_names:
                if table_name == 'sqlite_sequence':
                    continue  # Skip SQLite internal table
                
                table = Table(table_name)
                self._extract_table_info(conn, table)
                self.tables[table_name] = table
                
        finally:
            conn.close()
    
    def _get_table_names(self, conn: sqlite3.Connection) -> List[str]:
        """Get all table names from the database"""
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
        return [row[0] for row in cursor.fetchall()]
    
    def _extract_table_info(self, conn: sqlite3.Connection, table: Table):
        """Extract all information for a specific table"""
        self._extract_columns(conn, table)
        self._extract_foreign_keys(conn, table)
        self._extract_indexes(conn, table)
    
    def _extract_columns(self, conn: sqlite3.Connection, table: Table):
        """Extract column information for a table"""
        cursor = conn.cursor()
        cursor.execute(f"PRAGMA table_info({table.name})")
        
        for row in cursor.fetchall():
            col_id, name, data_type, not_null, default_val, primary_key = row
            column = Column(
                name=name,
                data_type=data_type,
                not_null=bool(not_null),
                default_value=default_val,
                primary_key=bool(primary_key)
            )
            table.add_column(column)
    
    def _extract_foreign_keys(self, conn: sqlite3.Connection, table: Table):
        """Extract foreign key information for a table"""
        cursor = conn.cursor()
        cursor.execute(f"PRAGMA foreign_key_list({table.name})")
        
        for row in cursor.fetchall():
            # Handle different SQLite versions that may return different numbers of columns
            if len(row) >= 7:
                fk_id, seq, ref_table, from_col, to_col, on_update, on_delete = row[:7]
            else:
                # Fallback for older SQLite versions
                fk_id, seq, ref_table, from_col, to_col = row[:5]
                on_update = 'NO ACTION'
                on_delete = 'NO ACTION'
            
            foreign_key = ForeignKey(
                from_column=from_col,
                to_table=ref_table,
                to_column=to_col,
                on_update=on_update,
                on_delete=on_delete
            )
            table.add_foreign_key(foreign_key)
    
    def _extract_indexes(self, conn: sqlite3.Connection, table: Table):
        """Extract index information for a table"""
        cursor = conn.cursor()
        cursor.execute(f"PRAGMA index_list({table.name})")
        
        for row in cursor.fetchall():
            # Only use the first three columns: seq, name, unique
            seq, name, unique = row[:3]
            if name.startswith('sqlite_autoindex_'):
                continue  # Skip auto-generated indexes
            
            index = Index(
                name=name,
                unique=bool(unique)
            )
            table.add_index(index)


class MermaidDiagramGenerator:
    """Generates Mermaid ER diagrams from database schema"""
    
    def __init__(self, schema: DatabaseSchema):
        self.schema = schema
    
    def generate_complete_diagram(self) -> str:
        """Generate complete Mermaid diagram with all tables and relationships"""
        lines = ["```mermaid", "erDiagram"]
        
        # Add all tables
        for table_name in sorted(self.schema.tables.keys()):
            table = self.schema.tables[table_name]
            lines.extend(table.to_complete_mermaid())
        
        # Add relationships
        lines.extend(["", "    %% Relationships"])
        for table_name in sorted(self.schema.tables.keys()):
            table = self.schema.tables[table_name]
            for fk in table.foreign_keys:
                lines.append(fk.to_mermaid_relationship(table.name))
        
        lines.append("```")
        return "\n".join(lines)
    
    def generate_relationship_diagram(self) -> str:
        """Generate relationship diagram with only foreign key tables and relationships"""
        lines = ["```mermaid", "erDiagram"]
        
        # Add only tables with foreign keys
        for table_name in sorted(self.schema.tables.keys()):
            table = self.schema.tables[table_name]
            if table.foreign_keys:
                lines.extend(table.to_relationship_mermaid())
        
        # Add relationships
        lines.extend(["", "    %% Foreign Key Relationships"])
        for table_name in sorted(self.schema.tables.keys()):
            table = self.schema.tables[table_name]
            for fk in table.foreign_keys:
                lines.append(fk.to_mermaid_relationship(table.name))
        
        lines.append("```")
        return "\n".join(lines)


class SchemaSummaryGenerator:
    """Generates schema summary documentation"""
    
    def __init__(self, schema: DatabaseSchema):
        self.schema = schema
    
    def generate_summary(self) -> str:
        """Generate complete schema summary"""
        lines = ["# Database Schema Summary", ""]
        
        for table_name in sorted(self.schema.tables.keys()):
            table = self.schema.tables[table_name]
            lines.extend(table.to_summary_section())
        
        return "\n".join(lines)


class DatabaseDiagramGenerator:
    """Main class to orchestrate the diagram generation process"""
    
    def __init__(self, output_dir: Path = None):
        self.output_dir = output_dir or Path(__file__).parent / "diagrams"
        if not self.output_dir.exists():
            self.output_dir.mkdir(parents=True, exist_ok=True)
    
    def get_database_path(self) -> Path:
        """Get the path to the SQLite database file"""
        # The database is typically in the instance directory
        instance_path = Path("instance")
        if instance_path.exists():
            db_files = list(instance_path.glob("*.db"))
            if db_files:
                return db_files[0]
        
        # Fallback to app.db in the root directory
        root_db = Path("app.db")
        if root_db.exists():
            return root_db
        
        raise FileNotFoundError("Could not find SQLite database file")
    
    def generate_diagrams(self) -> Tuple[str, str, str]:
        """Generate all diagrams and summaries"""
        # Get database path
        db_path = self.get_database_path()
        print(f"Found database at: {db_path}")
        
        # Extract schema
        print("Extracting database schema...")
        schema = DatabaseSchema(db_path)
        schema.extract_schema()
        
        # Generate diagrams
        print("Generating Mermaid diagrams...")
        diagram_generator = MermaidDiagramGenerator(schema)
        complete_diagram = diagram_generator.generate_complete_diagram()
        relationship_diagram = diagram_generator.generate_relationship_diagram()
        
        # Generate summary
        print("Generating schema summary...")
        summary_generator = SchemaSummaryGenerator(schema)
        schema_summary = summary_generator.generate_summary()
        
        return complete_diagram, relationship_diagram, schema_summary
    
    def write_output_files(self, complete_diagram: str, relationship_diagram: str, schema_summary: str):
        """Write all output files"""
        # Write complete diagram
        complete_diagram_path = self.output_dir / "database_diagram_complete.md"
        complete_diagram_path.write_text(
            "# Database Schema - Complete Mermaid Diagram\n\n"
            f"{complete_diagram}\n"
        )
        
        # Write relationship diagram
        relationships_path = self.output_dir / "database_diagram_relationships.md"
        relationships_path.write_text(
            "# Database Schema - Relationship Diagram (Foreign Keys Only)\n\n"
            f"{relationship_diagram}\n"
        )
        
        # Write schema summary
        summary_path = self.output_dir / "database_schema_summary.md"
        summary_path.write_text(schema_summary)
        
        print("Generated files:")
        print(f"- {complete_diagram_path}")
        print(f"- {relationships_path}")
        print(f"- {summary_path}")
        
        # Also print the relationship diagram to console
        print("\n" + "="*50)
        print("RELATIONSHIP DIAGRAM (Foreign Keys Only):")
        print("="*50)
        print(relationship_diagram)


def main():
    """Main function to generate the database diagram"""
    
    try:
        generator = DatabaseDiagramGenerator()
        complete_diagram, relationship_diagram, schema_summary = generator.generate_diagrams()
        generator.write_output_files(complete_diagram, relationship_diagram, schema_summary)
        
    except FileNotFoundError as e:
        print(f"Error: {e}")
        print("Please ensure the database file exists and the application has been initialized.")
        sys.exit(1)
    except Exception as e:
        print(f"Error generating diagram: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
