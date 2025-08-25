from app.models.core.user_created_base import UserCreatedBase
from app import db
from datetime import datetime

class MaintenancePlan(UserCreatedBase):
    __tablename__ = 'maintenance_plans'
    
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=True)
    asset_type_id = db.Column(db.Integer, db.ForeignKey('asset_types.id'), nullable=False)
    model_id = db.Column(db.Integer, db.ForeignKey('make_models.id'), nullable=True)
    status = db.Column(db.String(20), default='Active')  # Active/Inactive
    frequency_type = db.Column(db.String(20), nullable=False)  # Time-based, Meter-based, Condition-based
    frequency_value = db.Column(db.Float, nullable=False)
    
    # Relationships
    asset_type = db.relationship('AssetType', backref='maintenance_plans')
    model = db.relationship('MakeModel', backref='maintenance_plans')
    template_action_sets = db.relationship('TemplateActionSet', backref='maintenance_plan', lazy='dynamic')
    maintenance_event_sets = db.relationship('MaintenanceEventSet', lazy='dynamic')
    
    def __repr__(self):
        return f'<MaintenancePlan {self.name}>'
    
    @property
    def is_active(self):
        return self.status == 'Active'
    
    def create_maintenance_event(self, asset_id, scheduled_date=None):
        """Create a maintenance event from this plan"""
        from .maintenance_event_set import MaintenanceEventSet
        
        maintenance_event_set = MaintenanceEventSet(
            maintenance_plan_id=self.id,
            asset_id=asset_id,
            scheduled_date=scheduled_date or datetime.utcnow(),
            description=f"Maintenance event created from plan: {self.name}",
            created_by_id=self.created_by_id
        )

        
        return maintenance_event_set.event_id
