from app import db
from datetime import datetime
from app.models.core.data_insertion_mixin import DataInsertionMixin
from app.models.core.user_created_base import UserCreatedBase

class Event(UserCreatedBase, DataInsertionMixin, db.Model):
    __tablename__ = 'events'
    
    id = db.Column(db.Integer, primary_key=True)
    event_type = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    asset_id = db.Column(db.Integer, db.ForeignKey('assets.id'), nullable=True)
    major_location_id = db.Column(db.Integer, db.ForeignKey('major_locations.id'), nullable=True)
    
    # Relationships (no backrefs)
    user = db.relationship('User', foreign_keys=[user_id], overlaps="events")
    asset = db.relationship('Asset', overlaps="asset_ref,events")
    major_location = db.relationship('MajorLocation')
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Auto-set major_location_id from asset if not provided
        if self.asset_id and not self.major_location_id:
            from app.models.core.asset import Asset
            asset = Asset.query.get(self.asset_id)
            if asset and asset.major_location_id:
                self.major_location_id = asset.major_location_id
    
    def __repr__(self):
        return f'<Event {self.event_type}: {self.description}>' 