from app import db
from datetime import datetime

class Event(db.Model):
    __tablename__ = 'events'
    
    event_id = db.Column(db.Integer, primary_key=True)
    parent_id = db.Column(db.Integer, db.ForeignKey('events.event_id'))
    asset_id = db.Column(db.Integer, db.ForeignKey('assets.asset_id'))
    location_id = db.Column(db.Integer, db.ForeignKey('locations.location_id'))
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'))
    created_by = db.Column(db.Integer, db.ForeignKey('users.user_id'))
    event_type = db.Column(db.String(50), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())
    updated_at = db.Column(db.DateTime, default=db.func.current_timestamp(), onupdate=db.func.current_timestamp())

    # Relationships
    asset = db.relationship('Asset', backref='events')
    location = db.relationship('Location', backref='events')
    user = db.relationship('User', foreign_keys=[user_id], backref='user_events')
    creator = db.relationship('User', foreign_keys=[created_by], backref='created_events')
    parent = db.relationship('Event', remote_side=[event_id], backref='children')

    def to_dict(self):
        return {
            'event_id': self.event_id,
            'parent_id': self.parent_id,
            'asset_id': self.asset_id,
            'location_id': self.location_id,
            'user_id': self.user_id,
            'created_by': self.created_by,
            'event_type': self.event_type,
            'title': self.title,
            'description': self.description,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'asset': self.asset.common_name if self.asset else None,
            'location': self.location.common_name if self.location else None,
            'user': self.user.display_name if self.user else None,
            'creator': self.creator.display_name if self.creator else None
        }

    def __repr__(self):
        return f'<Event {self.event_type}: {self.title}>' 