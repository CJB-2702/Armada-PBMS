from app.models.core.user_created_base import UserCreatedBase
from app.models.maintenance.virtual_action_item import VirtualActionItem
from app import db
from datetime import datetime

class Action(VirtualActionItem):
    """base class for all actions"""
    __tablename__ = 'actions'

    # Action-specific fields
    scheduled_start_time = db.Column(db.DateTime, nullable=True)
    start_time = db.Column(db.DateTime, nullable=True)
    end_time = db.Column(db.DateTime, nullable=True)
    actual_billable_hours = db.Column(db.Float, nullable=True) 
    completion_notes = db.Column(db.Text, nullable=True)
    
    # Foreign Keys
    maintenance_event_set_id = db.Column(db.Integer, db.ForeignKey('maintenance_event_sets.id'), nullable=False)
    template_action_item_id = db.Column(db.Integer, db.ForeignKey('template_action_items.id'), nullable=False)
    
    # Relationships
    template_action_item = db.relationship('TemplateActionItem', backref='actions')
    
    def __repr__(self):
        return f'<Action {self.action_name}: {self.status}>'
    
    @property
    def is_skipped(self):
        return self.status == 'Skipped'
    
    def start_action(self, user_id):
        """Start the action"""
        super().start_action(user_id)  # Call parent method
        self.start_time = datetime.utcnow()
    
    def complete_action(self, user_id, notes=None):
        """Complete the action"""
        super().complete_action(user_id)  # Call parent method
        self.end_time = datetime.utcnow()
        self.completion_notes = notes
        
        # Calculate duration if start time exists
        if self.start_time and self.end_time:
            duration = (self.end_time - self.start_time).total_seconds() / 3600
            self.actual_billable_hours = round(duration, 2)
    
    def skip_action(self, user_id, reason=None):
        """Skip the action"""
        self.status = 'Skipped'
        self.completion_notes = f"Skipped: {reason}" if reason else "Skipped"
        self.updated_by_id = user_id
    
    def get_total_part_cost(self):
        """Calculate total cost of parts used"""
        total = 0
        for part_demand in self.get_part_demands():
            if hasattr(part_demand, 'expected_cost') and part_demand.expected_cost:
                total += part_demand.expected_cost
        return total
    
    def get_part_demands(self):
        """Get all part demands for the action using composition"""
        from app.models.maintenance.base.part_demand_to_action_references import PartDemandToActionReference
        return PartDemandToActionReference.get_part_demands_for_action(self.id)
    
    def get_part_demands_by_sequence(self):
        """Get all part demands for the action ordered by sequence order"""
        from app.models.maintenance.base.part_demand_to_action_references import PartDemandToActionReference
        references = PartDemandToActionReference.query.filter_by(action_id=self.id).order_by(PartDemandToActionReference.sequence_order).all()
        return [ref.part_demand for ref in references]
    
    def add_part_demand(self, part_demand_id, user_id, sequence_order=1, notes=None):
        """Add a part demand to this action"""
        from app.models.maintenance.base.part_demand_to_action_references import PartDemandToActionReference
        return PartDemandToActionReference.create_reference(
            action_id=self.id,
            part_demand_id=part_demand_id,
            user_id=user_id,
            sequence_order=sequence_order,
            notes=notes
        )
    
    def remove_part_demand(self, part_demand_id):
        """Remove a part demand from this action"""
        from app.models.maintenance.base.part_demand_to_action_references import PartDemandToActionReference
        return PartDemandToActionReference.remove_reference(self.id, part_demand_id)
