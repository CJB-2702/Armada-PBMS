import json
import os
from pathlib import Path
from typing import Dict, List, Any
from sqlalchemy.orm import Session
from app.core.config import settings
from app.models.event import EventType, FormType, FormTypeEventMapping

def load_json_file(file_path: str) -> Dict[str, Any]:
    """Load and parse a JSON file."""
    with open(file_path, 'r') as f:
        return json.load(f)

def load_default_data(db: Session) -> None:
    """Load default data into the database if in debug mode."""
    if not settings.DEBUG:
        return

    # Get the directory containing this file
    current_dir = Path(__file__).parent
    default_data_dir = current_dir / "default_data"

    # Load event types
    event_types_file = default_data_dir / "event_types.json"
    if event_types_file.exists():
        event_types_data = load_json_file(str(event_types_file))
        for event_type_data in event_types_data["event_types"]:
            # Check if event type already exists
            existing = db.query(EventType).filter(
                EventType.major_type == event_type_data["major_type"],
                EventType.minor_type == event_type_data["minor_type"]
            ).first()
            
            if not existing:
                event_type = EventType(**event_type_data)
                db.add(event_type)

    # Load form types and mappings
    form_types_file = default_data_dir / "form_types.json"
    if form_types_file.exists():
        form_data = load_json_file(str(form_types_file))
        
        # Load form types
        for form_type_data in form_data["form_types"]:
            # Check if form type already exists
            existing = db.query(FormType).filter(
                FormType.name == form_type_data["name"],
                FormType.version == form_type_data["version"]
            ).first()
            
            if not existing:
                form_type = FormType(**form_type_data)
                db.add(form_type)
                db.flush()  # Flush to get the form_type_row_id
        
        # Load form mappings
        for mapping_data in form_data["form_mappings"]:
            # Check if mapping already exists
            existing = db.query(FormTypeEventMapping).filter(
                FormTypeEventMapping.form_type_row_id == mapping_data["form_type_row_id"],
                FormTypeEventMapping.major_event_type == mapping_data["major_event_type"],
                FormTypeEventMapping.minor_event_type == mapping_data["minor_event_type"]
            ).first()
            
            if not existing:
                mapping = FormTypeEventMapping(**mapping_data)
                db.add(mapping)

    try:
        db.commit()
    except Exception as e:
        db.rollback()
        raise Exception(f"Error loading default data: {str(e)}")

def init_default_data(db: Session) -> None:
    """Initialize default data in the database."""
    if settings.DEBUG:
        load_default_data(db) 