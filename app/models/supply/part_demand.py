from app.models.core.user_created_base import UserCreatedBase
from app.models.supply.virtual_part_demand import VirtualPartDemand
from app import db
from datetime import datetime

class PartDemand(VirtualPartDemand):
    __tablename__ = 'part_demands'
    
    # PartDemand-specific fields
    quantity_used = db.Column(db.Float, nullable=True)
    unit_cost = db.Column(db.Float, nullable=True)
    total_cost = db.Column(db.Float, nullable=True)
    issued_date = db.Column(db.DateTime, nullable=True)
    notes = db.Column(db.Text, nullable=True)
    
    # PartDemand-specific foreign keys
    issued_by_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    
    # PartDemand-specific relationships
    issued_by = db.relationship('User', foreign_keys=[issued_by_id], overlaps="issued_part_demands")
    
    def __repr__(self):
        return f'<PartDemand {self.part.part_name if self.part else "Unknown"}: {self.quantity_required}>'
    
    @property
    def quantity_remaining(self):
        """Calculate remaining quantity to be used"""
        if self.quantity_used is None:
            return self.quantity_required
        return max(0, self.quantity_required - self.quantity_used)
    
    def approve(self, user_id):
        """Approve the part demand"""
        super().approve(user_id)  # Call parent method
    
    def issue(self, user_id, quantity=None):
        """Issue the part demand"""
        super().issue(user_id)  # Call parent method
        self.issued_date = datetime.utcnow()
        self.issued_by_id = user_id
        
        # Set unit cost from part if available
        if self.part and self.part.unit_cost:
            self.unit_cost = self.part.unit_cost
    
    def consume(self, quantity_used, user_id):
        """Consume parts and update stock"""
        if quantity_used > self.quantity_required:
            raise ValueError("Quantity used cannot exceed quantity required")
        
        self.quantity_used = quantity_used
        super().consume(user_id)  # Call parent method
        
        # Calculate total cost
        if self.unit_cost:
            self.total_cost = self.unit_cost * quantity_used
        
        # Update part stock level
        if self.part:
            self.part.adjust_stock(quantity_used, 'subtract', user_id)
    
    def calculate_cost(self):
        """Calculate total cost based on quantity used and unit cost"""
        if self.unit_cost and self.quantity_used:
            self.total_cost = self.unit_cost * self.quantity_used
        return self.total_cost
