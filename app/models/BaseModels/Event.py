from datetime import datetime
from app.extensions import db
from app.utils.logger import get_logger
from app.models.BaseModels.ProtoClasses import UserCreated, Types

logger = get_logger()

required_event_types = [
            {
                "row_id": 0,
                "name": "System",
                "description": "System events",
                "created_by": 0
            },
            {
                "row_id": 1,
                "name": "General",
                "description": "Basic Events, only a title and description",
                "created_by": 0
            }
        ]

class EventTypes(Types):
    __tablename__ = 'types_events'
    
    def get_protected_types(self):
        """Get the list of protected event types that cannot be deleted
        
        Returns:
            list: List of event type values that are protected from deletion
        """
        return ['System', 'General']


class Event(UserCreated):
    __tablename__ = 'events'
    
    title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text)
    event_type = db.Column(db.String(64), nullable=False, default='General')
    status = db.Column(db.String(50), nullable=False, default='Completed')
    location_UID = db.Column(db.String(50), db.ForeignKey('MajorLocations.UID'), default="SYSTEM")
    
    
    
    def __init__(self, title, description, event_type, status='pending', created_by=0, location_UID='SYSTEM'):
        self.title = title
        self.description = description
        self.event_type = event_type
        self.status = status
        self.location_UID = location_UID
        self.created_by = created_by
        self.updated_by = created_by
        
        logger.debug(
            'Creating event',
            extra={'log_data': {
                'title': title,
                'event_type': event_type,
                'status': status,
                'location_UID': location_UID,
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
        self.updated_at = datetime.now()
        
        logger.debug(
            'Updating event',
            extra={'log_data': {
                'event_id': self.row_id,
                'old_values': old_values,
                'new_values': kwargs
            }}
        )