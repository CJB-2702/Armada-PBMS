from app.data.core.user_created_base import UserCreatedBase
from app.data.maintenance.virtual_action_set import VirtualActionSet
from app import db
from sqlalchemy.orm import relationship

class TemplateActionSet(VirtualActionSet):
    __tablename__ = 'template_action_sets'
    
    # Foreign Keys
    maintenance_plan_id = db.Column(db.Integer, db.ForeignKey('maintenance_plans.id'), nullable=True)
    
    # Relationships
    template_action_items = relationship(
        'TemplateActionItem', 
        back_populates='template_action_set',
        lazy='selectin',
        order_by='TemplateActionItem.sequence_order'
    )
    maintenance_plans = relationship(
        'MaintenancePlan',
        back_populates='template_action_set',
        foreign_keys='MaintenancePlan.template_action_set_id',
        lazy='dynamic'
    )
    
    def __repr__(self):
        return f'<TemplateActionSet {self.task_name}>'
