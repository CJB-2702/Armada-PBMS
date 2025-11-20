from app.data.core.user_created_base import UserCreatedBase
from app import db
from sqlalchemy.orm import relationship

class MaintenancePlan(UserCreatedBase):
    __tablename__ = 'maintenance_plans'
    
    #header fields
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=True)
    asset_type_id = db.Column(db.Integer, db.ForeignKey('asset_types.id'), nullable=False)
    model_id = db.Column(db.Integer, db.ForeignKey('make_models.id'), nullable=True)
    status = db.Column(db.String(20), default='Active', nullable=False)

    #task to be assigned
    template_action_set_id = db.Column(db.Integer, db.ForeignKey('template_action_sets.id'), nullable=False)

    #frequency fields
    frequency_type = db.Column(db.String(20), nullable=False)
    delta_hours = db.Column(db.Float, nullable=True)
    delta_m1 = db.Column(db.Float, nullable=True)
    delta_m2 = db.Column(db.Float, nullable=True)
    delta_m3 = db.Column(db.Float, nullable=True)
    delta_m4 = db.Column(db.Float, nullable=True)
    
    # Improved relationships with proper loading strategies
    asset_type = relationship('AssetType', backref='maintenance_plans')
    model = relationship('MakeModel', backref='maintenance_plans')
    template_action_set = relationship(
        'TemplateActionSet', 
        foreign_keys=[template_action_set_id],
        back_populates='maintenance_plans'
    )
    maintenance_action_sets = relationship('MaintenanceActionSet', back_populates='maintenance_plan')

    def __repr__(self):
        return f'<MaintenancePlan {self.name}>'
    
    #-------------------------------- Getters and Setters --------------------------------
    
    def _set_status(self, value, user_id=None):
        """Set status with comment tracking"""
        old_value = self.status
        self.status = value
        if user_id and old_value != value:
            # Note: MaintenancePlan doesn't have direct comment access, 
            # but could be logged to system events
            pass
    
    def _set_frequency_type(self, value, user_id=None):
        """Set frequency type with comment tracking"""
        old_value = self.frequency_type
        self.frequency_type = value
        if user_id and old_value != value:
            # Note: MaintenancePlan doesn't have direct comment access
            pass
    
    # Properties for getters
    @property
    def is_active(self):
        return self.status == 'Active'
    
    @property
    def is_inactive(self):
        return self.status == 'Inactive'
    
    @property
    def is_archived(self):
        return self.status == 'Archived'
    
    @property
    def has_model_specificity(self):
        """Check if plan is specific to a model"""
        return self.model_id is not None
    
    @property
    def is_time_based(self):
        """Check if plan is time-based"""
        return self.frequency_type == 'Time-based'
    
    @property
    def is_mileage_based(self):
        """Check if plan is mileage-based"""
        return self.frequency_type == 'Mileage-based'
    
    # Note: Creation logic moved to MaintenancePlanFactory
        
