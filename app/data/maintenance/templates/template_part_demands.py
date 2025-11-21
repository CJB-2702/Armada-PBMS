from app.data.maintenance.virtual_part_demand import VirtualPartDemand
from app import db
from sqlalchemy.orm import relationship

class TemplatePartDemand(VirtualPartDemand):
    """
    Parts required for template actions
    Standalone copy - NO proto reference (allows template-specific customization)
    """
    __tablename__ = 'template_part_demands'
    
    # Parent reference - REQUIRED
    template_action_item_id = db.Column(db.Integer, db.ForeignKey('template_actions.id'), nullable=False)
    
    # Template-specific fields
    is_optional = db.Column(db.Boolean, default=False)
    sequence_order = db.Column(db.Integer, nullable=False, default=1)
    
    # Relationships
    template_action_item = relationship('TemplateActionItem', back_populates='template_part_demands')
    part = relationship('Part', foreign_keys='TemplatePartDemand.part_id', lazy='select')
    
    @property
    def is_required(self):
        return not self.is_optional
    
    def __repr__(self):
        part_name = self.part.part_name if self.part else "Unknown"
        return f'<TemplatePartDemand {self.id}: {part_name} x{self.quantity_required}>'
