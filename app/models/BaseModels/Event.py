from datetime import datetime
from app import db
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

    def __init__(self, value, description, created_by=None):
        super().__init__(value, description, created_by)


class Event(UserCreated):
    __tablename__ = 'events'
    
    title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text)
    event_type= db.Column(db.String(64), nullable=False, default='General')
    status = db.Column(db.String(50), nullable=False, default='Completed')
    
    
    
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
    
def create_initial_user_events():
    """Create events for SYSTEM and admin user creation if not already present. Should be called after users and event types are ensured."""
    from app.models.BaseModels.Users import User
    system_user = User.query.filter_by(username='SYSTEM').first()
    admin_user = User.query.filter_by(username='admin').first()
    from app.models.BaseModels.Event import Event
    created = False
    if system_user:
        existing_event = Event.query.filter_by(title=f"User Created: SYSTEM (ID: {system_user.row_id})").first()
        if not existing_event:
            event = Event(
                title=f"User Created: SYSTEM (ID: {system_user.row_id})",
                description=f"User created.\nUsername: SYSTEM\nDisplay Name: {system_user.display_name}\nEmail: {system_user.email}\nRole: {system_user.role}\nIs Admin: {system_user.is_admin}",
                event_type_id='SYSTEM',
                status='completed',
                created_by=0
            )
            db.session.add(event)
            created = True
    if admin_user:
        existing_event = Event.query.filter_by(title=f"User Created: admin (ID: {admin_user.row_id})").first()
        if not existing_event:
            event = Event(
                title=f"User Created: admin (ID: {admin_user.row_id})",
                description=f"User created.\nUsername: admin\nDisplay Name: {admin_user.display_name}\nEmail: {admin_user.email}\nRole: {admin_user.role}\nIs Admin: {admin_user.is_admin}",
                event_type_id='SYSTEM',
                status='completed',
                created_by=0
            )
            db.session.add(event)
            created = True
    if created:
        db.session.commit()

def ensure_required_event_types():
    """Ensure required event types exist in the database"""
    try:
        # Check if table exists by trying to query it
        EventTypes.query.first()

        # Table exists, check for required event types
        for event_data in Required_event_types:
            existing_event = EventTypes.query.filter_by(value=event_data['name']).first()
            if not existing_event:
                event = EventTypes(
                    value=event_data['name'],
                    description=event_data['description'],
                    created_by=event_data['created_by']
                )
                db.session.add(event)
                logger.info(f"Created required event type: {event_data['name']}")

        db.session.commit()
        logger.info("Required event types check completed")

    except Exception as e:
        # Table doesn't exist yet, that's okay
        logger.debug(f"Event types table not ready yet: {e}")
        pass