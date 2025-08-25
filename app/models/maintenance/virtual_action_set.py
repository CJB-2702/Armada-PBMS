from app.models.core.user_created_base import UserCreatedBase
from app import db
from datetime import datetime

class VirtualActionSet(UserCreatedBase):
    """Virtual action sets created from templates"""
    __abstract__ = True
    

    task_name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=True)
    sequence_order = db.Column(db.Integer, nullable=False, default=1)
    revision = db.Column(db.String(20), nullable=False, default='1')
    estimated_duration = db.Column(db.Float, nullable=True)
    staff_count = db.Column(db.Integer, nullable=False, default=1)
    parts_cost = db.Column(db.Float, nullable=True)
    labor_hours = db.Column(db.Float, nullable=True)
    safety_review_required = db.Column(db.Boolean, default=False)
    
    def __repr__(self):
        return f'<VirtualActionSet {self.template_action_set.set_name if self.template_action_set else "Unknown"}: {self.status}>'
    
    @property
    def is_not_started(self):
        return self.status == 'Not Started'
    
    @property
    def is_in_progress(self):
        return self.status == 'In Progress'
    
    @property
    def is_completed(self):
        return self.status == 'Completed'
    
    def start_action_set(self, user_id):
        """Start the virtual action set"""
        self.status = 'In Progress'
        self.progress = 0.0
        self.updated_by_id = user_id
    
    def update_progress(self, progress, user_id):
        """Update progress (0.0 to 1.0)"""
        self.progress = max(0.0, min(1.0, progress))
        self.updated_by_id = user_id
        
        if self.progress >= 1.0:
            self.status = 'Completed'
    
    def complete_action_set(self, user_id):
        """Complete the virtual action set"""
        self.status = 'Completed'
        self.progress = 1.0
        self.updated_by_id = user_id
    
    def calculate_progress_from_virtual_actions(self):
        """Calculate progress based on virtual action items"""
        virtual_actions = self.maintenance_event.virtual_action_items.filter_by(
            template_action_item_id=self.template_action_set.template_action_items
        ).all()
        
        if not virtual_actions:
            return 0.0
        
        completed_count = sum(1 for action in virtual_actions if action.is_completed)
        return completed_count / len(virtual_actions)
