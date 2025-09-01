from app.models.core.user_created_base import UserCreatedBase
from app import db
from datetime import datetime
from sqlalchemy import Index, UniqueConstraint, func
from sqlalchemy.orm import relationship, validates
from app.models.supply.part_demand import PartDemand
from app.models.maintenance.templates.template_part_demand import TemplatePartDemand

class PartDemandToActionReference(UserCreatedBase):
    """Reference table that links maintenance actions to part demands using composition pattern"""
    __tablename__ = 'part_demand_to_action_references'
    
    # Table constraints and indexes for better performance and data integrity
    __table_args__ = (
        UniqueConstraint('action_id', 'part_demand_id', name='uq_action_part_demand'),
        Index('ix_part_demand_action_sequence', 'action_id', 'sequence_order'),
        Index('ix_part_demand_references_action', 'action_id'),
        Index('ix_part_demand_references_part_demand', 'part_demand_id'),
    )
    
    # Foreign Keys
    action_id = db.Column(db.Integer, db.ForeignKey('actions.id'), nullable=False, index=True)
    part_demand_id = db.Column(db.Integer, db.ForeignKey('part_demands.id'), nullable=False, index=True)
    template_part_demand_id = db.Column(db.Integer, db.ForeignKey('template_part_demands.id'), nullable=True, index=True)
    
    # Optional fields for additional context
    sequence_order = db.Column(db.Integer, nullable=False, default=1)
    notes = db.Column(db.Text, nullable=True)
    
    # Improved relationships with proper loading strategies
    action = relationship('Action', back_populates='part_demand_references')
    part_demand = relationship('PartDemand', back_populates='action_references')
    template_part_demand = relationship('TemplatePartDemand', back_populates='action_references')

    def __init__(self, action_id, user_id, notes=None, template_part_demand_id=None, part_id=None, quantity=None, **kwargs):
        super().__init__(created_by_id=user_id, **kwargs)
        
        is_template = template_part_demand_id is not None
        is_part_tuple = part_id is not None and quantity is not None
        if (is_template and is_part_tuple) or (not is_template and not is_part_tuple):
            raise ValueError("Either template_part_demand_id or part_id and quantity must be provided")
        
        self.notes = notes
        self.action_id = action_id
        
        if template_part_demand_id:
            self.template_part_demand_id = template_part_demand_id
            template_part_demand = db.session.get(TemplatePartDemand, template_part_demand_id)
            part_id = template_part_demand.part_id
            quantity = template_part_demand.quantity_required
            
        part_demand = PartDemand(created_by_id=user_id, part_id=part_id, quantity_required=quantity, notes=notes)
        db.session.add(part_demand)
        db.session.flush()
        self.part_demand_id = part_demand.id


    @classmethod
    def add_part_demand_from_template(cls, action_id, template_part_demand, user_id, notes=None):
        ref = cls(action_id, user_id, notes=notes, template_part_demand_id=template_part_demand.id)
        db.session.add(ref)
        return ref
    
    @classmethod
    def add_part_demand_for_action(cls, action_id, part_id, quantity_required, user_id, notes=None):
        ref = cls(action_id, user_id, notes=notes, part_id=part_id, quantity=quantity_required)
        db.session.add(ref)
        return ref

    def __repr__(self):
        return f'<PartDemandToActionReference {self.part_demand.part.part_name} for {self.action.action_name}>'

    def remove_part_demand(self):
        db.session.delete(self)
        db.session.delete(self.part_demand)
        db.session.commit()
    
    def update_part_demand(self, part_id, quantity, notes=None):
        if quantity <= 0:
            self.remove_part_demand()
            return
        self.part_demand.part_id = part_id
        self.part_demand.quantity_required = quantity
        self.part_demand.notes = notes
        self.part_demand.updated_by_id = self.created_by_id
        self.part_demand.updated_at = datetime.utcnow()
        db.session.commit()

    def reduce_part_demand(self, quantity):
        new_quantity = self.part_demand.quantity_required - quantity
        if new_quantity <= 0:
            self.remove_part_demand()
        else:
            self.part_demand.quantity_required = new_quantity
            db.session.commit()

    