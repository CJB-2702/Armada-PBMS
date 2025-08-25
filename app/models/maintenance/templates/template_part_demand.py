from app.models.supply.virtual_part_demand import VirtualPartDemand
from app import db
from datetime import datetime

class TemplatePartDemand(VirtualPartDemand):
    __tablename__ = 'template_part_demands'
    
    # Template-specific fields
    is_optional = db.Column(db.Boolean, default=False)
    
    # Foreign Keys
    template_action_item_id = db.Column(db.Integer, db.ForeignKey('template_action_items.id'), nullable=False)
    
    # Relationships
    template_action_item = db.relationship('TemplateActionItem', backref='template_part_demands')
    
    def __repr__(self):
        return f'<TemplatePartDemand {self.part.part_name if self.part else "Unknown"}: {self.quantity_required}>'
    
    @property
    def is_required(self):
        return not self.is_optional
    
    def create_part_demand(self, action_id, user_id):
        """Create a part demand from this template"""
        from app.models.supply.parts_demand import PartDemand
        
        part_demand = PartDemand(
            action_id=action_id,
            part_id=self.part_id,
            template_part_demand_id=self.id,
            quantity_required=self.quantity_required,
            status='Requested',
            created_by_id=user_id,
            notes=f"Created from template part demand {self.id}"
        )
        
        return part_demand
