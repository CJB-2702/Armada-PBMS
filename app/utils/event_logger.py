from app.models.event import Event
from app import db
import json
from functools import wraps

def log_event(event_type, title, description=None):
    """
    Decorator to log events when a model is created/updated
    
    Args:
        event_type (str): Type of event (e.g., 'asset_created', 'maintenance')
        title (str): Title of the event
        description (str, optional): Description of the event
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Get the result of the original function
            result = func(*args, **kwargs)
            
            # Create the event
            event = Event(
                event_type=event_type,
                title=title,
                description=description,
                created_by=kwargs.get('created_by', 1),  # Default to user 1 if not specified
                asset_id=kwargs.get('asset_id'),  # Will be None if not specified
                location_id=kwargs.get('location_id'),  # Will be None if not specified
                user_id=kwargs.get('user_id')  # Will be None if not specified
            )
            
            # Add the event to the session
            db.session.add(event)
            db.session.commit()
            
            return result
        return wrapper
    return decorator

def log_creation_event(entity_type, entity_data, user_id):
    """
    Log a creation event with JSON content
    
    Args:
        entity_type (str): Type of entity being created (asset, location, user)
        entity_data (dict): Dictionary of entity data to log
        user_id (int): ID of the user creating the entity
    """
    # Create event title
    title = f"New {entity_type.title()} Created"
    
    # Convert entity_data to JSON string
    content = json.dumps(entity_data, indent=2)
    
    # Create the event
    event = Event(
        event_type=f"{entity_type}_created",
        title=title,
        description=content,
        created_by=user_id,
        asset_id=1  # Using asset_id=1 as meta for now
    )
    
    db.session.add(event)
    db.session.commit()
    
    return event 