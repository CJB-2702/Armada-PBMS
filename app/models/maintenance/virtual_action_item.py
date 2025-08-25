from app.models.core.user_created_base import UserCreatedBase
from app import db
from datetime import datetime

class VirtualActionItem(UserCreatedBase):
    """Virtual action items created from templates"""
    __abstract__ = True
    
    action_name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=True) 
    estimated_duration = db.Column(db.Float, nullable=True)  # in hours
    safety_notes = db.Column(db.Text, nullable=True)
    instructions = db.Column(db.Text, nullable=True)
    item_name = db.Column(db.String(200), nullable=False)
    staff_count = db.Column(db.Integer, nullable=False, default=1)
    required_skills = db.Column(db.Text, nullable=True)
    
    def __repr__(self):
        return f'<VirtualActionItem {self.template_action_item.item_name if self.template_action_item else "Unknown"}: {self.status}>'
    
    @property
    def is_not_started(self):
        return self.status == 'Not Started'
    
    @property
    def is_in_progress(self):
        return self.status == 'In Progress'
    
    @property
    def is_completed(self):
        return self.status == 'Completed'
    
    def start_action(self, user_id):
        """Start the virtual action item"""
        self.status = 'In Progress'
        self.progress = 0.0
        self.assigned_to_id = user_id
        self.updated_by_id = user_id
    
    def update_progress(self, progress, user_id):
        """Update progress (0.0 to 1.0)"""
        self.progress = max(0.0, min(1.0, progress))
        self.updated_by_id = user_id
        
        if self.progress >= 1.0:
            self.status = 'Completed'
    
    def complete_action(self, user_id):
        """Complete the virtual action item"""
        self.status = 'Completed'
        self.progress = 1.0
        self.updated_by_id = user_id
