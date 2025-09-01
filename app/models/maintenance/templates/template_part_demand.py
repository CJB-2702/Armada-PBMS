from app.models.supply.virtual_part_demand import VirtualPartDemand
from app import db
from datetime import datetime

class TemplatePartDemand(VirtualPartDemand):
    __tablename__ = 'template_part_demands'
    
    # Template-specific fields
    is_optional = db.Column(db.Boolean, default=False) 
    sequence_order = db.Column(db.Integer, nullable=False, default=1)
    
    # Foreign Keys
    template_action_item_id = db.Column(db.Integer, db.ForeignKey('template_action_items.id'), nullable=False)
    
    # Relationships
    template_action_item = db.relationship('TemplateActionItem')
    part = db.relationship('Part')
    action_references = db.relationship('PartDemandToActionReference', back_populates='template_part_demand')
    
    def __repr__(self):
        return f'<TemplatePartDemand {self.part.part_name if self.part else "Unknown"}: {self.quantity_required}>'
    
    @property
    def is_required(self):
        return not self.is_optional
