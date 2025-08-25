from app.models.core.user_created_base import UserCreatedBase
from app import db
from datetime import datetime

class VirtualPartDemand(UserCreatedBase):
    """Virtual part demands created from templates"""
    __abstract__ = True

    part_id = db.Column(db.Integer, db.ForeignKey('parts.id'), nullable=False)
    notes = db.Column(db.Text, nullable=True)
    quantity_required = db.Column(db.Float, nullable=False, default=1.0)
    expected_cost = db.Column(db.Float, nullable=True)

    def calculate_expected_cost(self):
        """Calculate the expected cost of the part demand"""
        if self.part and self.part.unit_cost:
            self.expected_cost = self.quantity_required * self.part.unit_cost
        else:
            self.expected_cost = None
