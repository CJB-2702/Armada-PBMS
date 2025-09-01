from app.models.core.user_created_base import UserCreatedBase
from app.models.supply.virtual_part_demand import VirtualPartDemand
from app import db
from datetime import datetime

class PartDemand(VirtualPartDemand):
    __tablename__ = 'part_demands'
    
    requested_by_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    requested_date = db.Column(db.DateTime, nullable=True)

    approved_by_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    approved_date = db.Column(db.DateTime, nullable=True)

    status = db.Column(db.String(20), default='Requested') 

    # Relationships
    part = db.relationship('Part', overlaps='part_demands')
    requested_by = db.relationship('User', foreign_keys=[requested_by_id])
    approved_by = db.relationship('User', foreign_keys=[approved_by_id])
    # Note: action_references relationship will be added when maintenance module is integrated

    def __repr__(self):
        return f'<PartDemand {self.part.part_name if self.part else "Unknown"}: {self.quantity_required}>'
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.calculate_expected_cost()
