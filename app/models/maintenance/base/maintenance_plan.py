from app.models.core.user_created_base import UserCreatedBase
from app import db
from sqlalchemy.orm import relationship

class MaintenancePlan(UserCreatedBase):
    __tablename__ = 'maintenance_plans'
    
    #header fields
    name = db.Column(db.String(200), nullable=False, index=True)
    description = db.Column(db.Text, nullable=True)
    asset_type_id = db.Column(db.Integer, db.ForeignKey('asset_types.id'), nullable=False, index=True)
    model_id = db.Column(db.Integer, db.ForeignKey('make_models.id'), nullable=True)
    status = db.Column(db.String(20), default='Active', nullable=False, index=True)

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
    maintenance_event_sets = relationship(
        'MaintenanceEventSet', 
        back_populates='maintenance_plan',
        lazy='dynamic'
    )

    def __repr__(self):
        return f'<MaintenancePlan {self.name}>'

    def schedule_maintenance(self, asset_id, scheduled_date=None, user_id=None):
        #todo make class managers based off frequency type and delta fields to handle logic and scheduling
        pass
    
    
    def create_maintenance_event(self, asset_id, scheduled_date=None, user_id=None):
        """Create a maintenance event from this plan - using delegation pattern"""
        from app.models.maintenance.base.maintenance_event_set import MaintenanceEventSet

        maintenance_event_set = MaintenanceEventSet(
            maintenance_plan_id=self.id,
            template_action_set_id=self.template_action_set_id,
            asset_id=asset_id,
            scheduled_date=scheduled_date,
            created_by_id=user_id
        )
        db.session.add(maintenance_event_set)
        db.session.commit()
        
