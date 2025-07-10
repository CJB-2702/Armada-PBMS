from datetime import datetime
from app.extensions import db
from app.utils.logger import get_logger
from app.models.BaseModels.ProtoClasses import UserCreated, Types

import datetime

logger = get_logger()

Required_event_types = [
            {
                "name": "System",
                "description": "System events",
                "created_by": 0
            },
            {
                "name": "General",
                "description": "Basic Events, only a title and description",
                "created_by": 0
            }
        ]

class EventTypes(Types):
    __tablename__ = 'types_events'


class Event(UserCreated):
    __tablename__ = 'events'
    
    title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text)
    event_type_id = db.Column(db.String(64), nullable=False, default='General')
    status = db.Column(db.String(50), nullable=False, default='Completed')
    location = db.Column(db.Integer, db.ForeignKey('MajorLocations.row_id'), nullable=True, default=0)
    
    
    
    def __init__(self, title, description, event_type_id, status='pending', created_by=0):
        self.title = title
        self.description = description
        self.event_type_id = event_type_id
        self.status = status
        self.created_by = created_by
        self.updated_by = created_by
        
        logger.debug(
            'Creating event',
            extra={'log_data': {
                'title': title,
                'event_type_id': event_type_id,
                'status': status,
                'created_by': created_by
            }}
        )
    
    def __repr__(self):
        return f'<Event {self.title}>'
    
    def update(self, **kwargs):
        old_values = {key: getattr(self, key) for key in kwargs.keys() if hasattr(self, key)}
        
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
        self.updated_at = datetime.utcnow()
        
        logger.debug(
            'Updating event',
            extra={'log_data': {
                'event_id': self.event_row_id,
                'old_values': old_values,
                'new_values': kwargs
            }}
        )


def ensure_required_event_types():
    """Ensure required event types exist in the database"""
    logger.info("Starting Event Types initialization...")
    logger.info(f"Required event types to create: {len(Required_event_types)}")
    
    for event_data in Required_event_types:
        try:
            logger.info(f"Checking for event type: {event_data['name']}")
            existing_event = EventTypes.query.filter_by(value=event_data['name']).first()
            if not existing_event:
                logger.info(f"Creating event type: {event_data['name']}")
                event = EventTypes(
                    value=event_data['name'],
                    description=event_data['description'],
                    created_by=event_data['created_by']
                )
                db.session.add(event)
                logger.info(f"✓ Created required event type: {event_data['name']}")
            else:
                logger.info(f"✓ Event type already exists: {event_data['name']}")
        except Exception as e:
            logger.error(f"Error creating event type {event_data['name']}: {e}")
            continue
    
    try:
        db.session.commit()
        logger.info("✓ Event types database commit successful")
    except Exception as e:
        logger.error(f"Error committing event types to database: {e}")
        db.session.rollback()
        raise
    
    # Verify final count
    final_count = EventTypes.query.count()
    logger.info(f"Final event type count: {final_count}")
    logger.info("✓ Required event types check completed")


def create_initial_events():
    """Create all initial events if the events table is empty"""
    #ONLY RUN THIS AFTER ALL OTHER MODELS ARE CREATED
    #Rely on __init__.py to create the tables and insert the initial data for the other models
    logger.info("Starting Initial Events creation...")
    
    from app.models.BaseModels.Users import User
    from app.models.BaseModels.Locations import MajorLocation
    
    # Check if events table is empty
    try:
        event_count = Event.query.count()
        logger.info(f"Current event count: {event_count}")
        if event_count > 0:
            logger.info(f"Events table already has {event_count} events, skipping initial event creation")
            return
    except Exception as e:
        logger.error(f"Error checking event count: {e}")
        raise
    
    # Verify required data exists
    logger.info("Verifying required data for initial events...")
    try:
        system_user = User.query.filter_by(username='SYSTEM').first()
        admin_user = User.query.filter_by(username='admin').first()
        system_location = MajorLocation.query.filter_by(UID='SYSTEM').first()
        
        logger.info(f"SYSTEM user found: {system_user is not None}")
        logger.info(f"admin user found: {admin_user is not None}")
        logger.info(f"system location found: {system_location is not None}")
        
        if not system_user or not admin_user or not system_location:
            error_msg = "Required data not found for initial events creation"
            logger.error(error_msg)
            raise RuntimeError(error_msg)
    except Exception as e:
        logger.error(f"Error verifying required data: {e}")
        raise
    
    # Define all initial events in a dictionary
    logger.info("Creating initial events...")
    initial_events = [
        {
            "title": f"User Created: SYSTEM (ID: {system_user.row_id})",
            "description": f"User created.\nUsername: SYSTEM\nDisplay Name: {system_user.display_name}\nEmail: {system_user.email}\nRole: {system_user.role}\nIs Admin: {system_user.is_admin}",
            "event_type_id": "SYSTEM",
            "status": "completed",
            "created_by": 0
        },
        {
            "title": f"User Created: admin (ID: {admin_user.row_id})",
            "description": f"User created.\nUsername: admin\nDisplay Name: {admin_user.display_name}\nEmail: {admin_user.email}\nRole: {admin_user.role}\nIs Admin: {admin_user.is_admin}",
            "event_type_id": "SYSTEM",
            "status": "completed",
            "created_by": 0
        },
        {
            "title": f"System Location Created: {system_location.common_name} (ID: {system_location.row_id})",
            "description": f"System location created.\nUID: {system_location.UID}\nCommon Name: {system_location.common_name}\nDescription: {system_location.description}\nStatus: {system_location.status}",
            "event_type_id": "SYSTEM",
            "status": "completed",
            "created_by": 0
        }
    ]
    
    # Create all events
    try:
        for i, event_data in enumerate(initial_events, 1):
            logger.info(f"Creating event {i}/{len(initial_events)}: {event_data['title']}")
            event = Event(**event_data)
            db.session.add(event)
        
        db.session.commit()
        logger.info(f"✓ Created {len(initial_events)} initial events successfully")
    except Exception as e:
        logger.error(f"Error creating initial events: {e}")
        db.session.rollback()
        raise
    
    # Verify final count
    final_count = Event.query.count()
    logger.info(f"Final event count: {final_count}")
    logger.info("✓ Initial events creation completed")