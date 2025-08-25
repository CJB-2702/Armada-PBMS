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
    notes = db.Column(db.Text, nullable=True)
    completion_notes = db.Column(db.Text, nullable=True)
    
    # Foreign Keys
    maintenance_event_set_id = db.Column(db.Integer, db.ForeignKey('maintenance_event_sets.id'), nullable=False)
    template_action_item_id = db.Column(db.Integer, db.ForeignKey('template_action_items.id'), nullable=False)
    
    # Relationships
    template_action_item = db.relationship('TemplateActionItem', backref='actions')
    part_demands = db.relationship('PartDemand', lazy='dynamic')
    
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
        for part_demand in self.part_demands:
            if part_demand.total_cost:
                total += part_demand.total_cost
        return total
