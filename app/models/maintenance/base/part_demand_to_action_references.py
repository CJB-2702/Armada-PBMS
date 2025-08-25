from app.models.core.user_created_base import UserCreatedBase
from app import db
from datetime import datetime

class PartDemandToActionReference(UserCreatedBase):
    """Reference table that links maintenance actions to part demands using composition pattern"""
    __tablename__ = 'part_demand_to_action_references'
    
    # Foreign Keys
    action_id = db.Column(db.Integer, db.ForeignKey('actions.id'), nullable=False)
    part_demand_id = db.Column(db.Integer, db.ForeignKey('part_demands.id'), nullable=False)
    
    # Optional fields for additional context
    sequence_order = db.Column(db.Integer, nullable=True, default=1)
    notes = db.Column(db.Text, nullable=True)
    
    # Relationships
    action = db.relationship('Action', backref='part_demand_references')
    part_demand = db.relationship('PartDemand', backref='action_references')
    
    def __repr__(self):
        return f'<PartDemandToActionReference Action:{self.action_id} -> PartDemand:{self.part_demand_id}>'
    
    @classmethod
    def create_reference(cls, action_id, part_demand_id, user_id, sequence_order=1, notes=None):
        """Create a new reference between an action and a part demand"""
        reference = cls(
            action_id=action_id,
            part_demand_id=part_demand_id,
            sequence_order=sequence_order,
            notes=notes,
            created_by_id=user_id
        )
        db.session.add(reference)
        return reference
    
    @classmethod
    def get_part_demands_for_action(cls, action_id):
        """Get all part demands linked to a specific action"""
        references = cls.query.filter_by(action_id=action_id).order_by(cls.sequence_order).all()
        return [ref.part_demand for ref in references]
    
    @classmethod
    def get_actions_for_part_demand(cls, part_demand_id):
        """Get all actions linked to a specific part demand"""
        references = cls.query.filter_by(part_demand_id=part_demand_id).all()
        return [ref.action for ref in references]
    
    @classmethod
    def remove_reference(cls, action_id, part_demand_id):
        """Remove a specific reference between an action and part demand"""
        reference = cls.query.filter_by(
            action_id=action_id, 
            part_demand_id=part_demand_id
        ).first()
        if reference:
            db.session.delete(reference)
            return True
        return False
