#!/usr/bin/env python3
"""
Model Additional Dispatch Detail Table Set
Configuration container that defines additional dispatch detail table types for a specific model beyond what the asset type provides
"""

from app.models.core.user_created_base import UserCreatedBase
from app.logger import get_logger
logger = get_logger("asset_management.models.dispatching")
from app import db

class ModelAdditionalDispatchDetailTableSet(UserCreatedBase):
    """
    Configuration container that defines additional dispatch detail table types 
    for a specific model beyond what the asset type provides
    """
    __tablename__ = 'model_additional_dispatch_detail_table_sets'
    
    # Configuration fields
    make_model_id = db.Column(db.Integer, db.ForeignKey('make_models.id'), nullable=False)
    dispatch_detail_table_type = db.Column(db.String(100), nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    
    # Relationships
    make_model = db.relationship('MakeModel', backref='additional_dispatch_detail_table_sets')
    
    def __repr__(self):
        """String representation of the model additional dispatch detail table set"""
        return f'<ModelAdditionalDispatchDetailTableSet {self.make_model.make} {self.make_model.model}:{self.dispatch_detail_table_type}>'
    
    @classmethod
    def get_dispatch_detail_table_types_for_model(cls, make_model_id):
        """Get all dispatch detail table types configured for a specific model"""
        return cls.query.filter_by(
            make_model_id=make_model_id,
            is_active=True
        ).all()
    
    @classmethod
    def create_dispatch_detail_table_rows(cls, dispatch_id, make_model_id):
        """Create dispatch detail table rows based on model configurations"""
        try:
            # Get all dispatch detail table configurations for this model
            detail_configs = cls.get_dispatch_detail_table_types_for_model(make_model_id)
            
            for config in detail_configs:
                cls._create_single_dispatch_detail_row(config, dispatch_id)
                
        except Exception as e:
            logger.debug(f"Error creating model additional dispatch detail table rows for dispatch {dispatch_id}: {e}")
    
    @classmethod
    def _create_single_dispatch_detail_row(cls, config, dispatch_id):
        """Create a single dispatch detail table row based on configuration"""
        try:
            # Dispatch detail table registry mapping
            dispatch_detail_table_registry = {
                'vehicle_dispatch': 'app.models.dispatching.dispatch_details.vehicle_dispatch.VehicleDispatch',
                'truck_dispatch_checklist': 'app.models.dispatching.dispatch_details.truck_dispatch_checklist.TruckDispatchChecklist'
            }
            
            dispatch_detail_table_class_path = dispatch_detail_table_registry.get(config.dispatch_detail_table_type)
            if not dispatch_detail_table_class_path:
                logger.debug(f"Warning: Unknown dispatch detail table type '{config.dispatch_detail_table_type}'")
                return
            
            # Import the dispatch detail table class
            module_path, class_name = dispatch_detail_table_class_path.rsplit('.', 1)
            module = __import__(module_path, fromlist=[class_name])
            dispatch_detail_table_class = getattr(module, class_name)
            
            # Create the dispatch detail table row - check for duplicates first
            existing_row = dispatch_detail_table_class.query.filter_by(dispatch_id=dispatch_id).first()
            if existing_row:
                logger.debug(f"DEBUG: Dispatch detail row already exists for dispatch {dispatch_id}, skipping")
                return  # Already exists, don't create duplicate
            
            dispatch_detail_row = dispatch_detail_table_class(dispatch_id=dispatch_id)
            
            # Add to session (don't commit - let the main transaction handle it)
            db.session.add(dispatch_detail_row)
            
        except Exception as e:
            logger.debug(f"Error creating dispatch detail row for {config.dispatch_detail_table_type}: {e}")
            # Don't rollback here - let the main transaction handle it
