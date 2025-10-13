from app.models.core.user_created_base import UserCreatedBase
from app import db

class VirtualActionSet(UserCreatedBase):
    """Virtual action sets created from templates"""
    __abstract__ = True
    
    task_name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=True)
    sequence_order = db.Column(db.Integer, nullable=True, default=1)
    revision = db.Column(db.String(20), nullable=True, default='1')
    estimated_duration = db.Column(db.Float, nullable=True)
    staff_count = db.Column(db.Integer, nullable=True, default=1)
    parts_cost = db.Column(db.Float, nullable=True)
    labor_hours = db.Column(db.Float, nullable=True)
    safety_review_required = db.Column(db.Boolean, default=False)
