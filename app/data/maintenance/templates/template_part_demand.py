from app.data.maintenance.virtual_part_demand import VirtualPartDemand
from app import db
from datetime import datetime
from sqlalchemy.orm import relationship

class TemplatePartDemand(VirtualPartDemand):
    __tablename__ = 'template_part_demands'
    
    # Template-specific fields
    is_optional = db.Column(db.Boolean, default=False) 
    sequence_order = db.Column(db.Integer, nullable=False, default=1)
    
    # Foreign Keys
    template_action_item_id = db.Column(db.Integer, db.ForeignKey('template_action_items.id'), nullable=False)
    
    # Relationships
    template_action_item = db.relationship('TemplateActionItem', back_populates='template_part_demands')
    part = db.relationship('Part', foreign_keys='TemplatePartDemand.part_id')
    
    def __repr__(self):
        return f'<TemplatePartDemand {self.part.part_name if self.part else "Unknown"}: {self.quantity_required}>'
    
    @property
    def is_required(self):
        return not self.is_optional
