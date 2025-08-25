from app.models.core.user_created_base import UserCreatedBase
from app import db
from datetime import datetime

class VirtualPartDemand(UserCreatedBase):
    """Virtual part demands created from templates"""
    __tablename__ = 'virtual_part_demands'
    
    status = db.Column(db.String(20), default='Requested')
    quantity_required = db.Column(db.Float, nullable=False, default=1.0)
    
    # Foreign Keys
    template_part_demand_id = db.Column(db.Integer, db.ForeignKey('template_part_demands.id'), nullable=False)
    action_id = db.Column(db.Integer, db.ForeignKey('actions.id'), nullable=False)
    part_id = db.Column(db.Integer, db.ForeignKey('parts.id'), nullable=False)
    
    # Relationships
    template_part_demand = db.relationship('TemplatePartDemand', backref='virtual_part_demands')
    action = db.relationship('Action', backref='virtual_part_demands')
    part = db.relationship('Part', backref='virtual_part_demands')
    
    def __repr__(self):
        return f'<VirtualPartDemand {self.part.part_name if self.part else "Unknown"}: {self.quantity_required}>'
    
    @property
    def is_requested(self):
        return self.status == 'Requested'
    
    @property
    def is_approved(self):
        return self.status == 'Approved'
    
    @property
    def is_issued(self):
        return self.status == 'Issued'
    
    @property
    def is_consumed(self):
        return self.status == 'Consumed'
    
    def approve(self, user_id):
        """Approve the virtual part demand"""
        self.status = 'Approved'
        self.updated_by_id = user_id
    
    def issue(self, user_id):
        """Issue the virtual part demand"""
        self.status = 'Issued'
        self.updated_by_id = user_id
    
    def consume(self, user_id):
        """Consume the virtual part demand"""
        self.status = 'Consumed'
        self.updated_by_id = user_id
    
    def create_actual_part_demand(self, user_id):
        """Create an actual part demand from this virtual one"""
        from app.models.supply.parts_demand import PartDemand
        
        part_demand = PartDemand(
            action_id=self.action_id,
            part_id=self.part_id,
            template_part_demand_id=self.template_part_demand_id,
            quantity_required=self.quantity_required,
            status=self.status,
            created_by_id=user_id,
            notes=f"Created from virtual part demand {self.id}"
        )
        
        return part_demand
