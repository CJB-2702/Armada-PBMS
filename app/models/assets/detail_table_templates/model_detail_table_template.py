#!/usr/bin/env python3
"""
Model Detail Table Set
Configuration container that defines additional detail table types for a specific model beyond what the asset type provides
"""

from app.models.core.user_created_base import UserCreatedBase
from app.logger import get_logger
logger = get_logger("asset_management.models.assets")
from app import db

class ModelDetailTableTemplate(UserCreatedBase):
    """
    Configuration container that defines additional detail table types for a specific model beyond what the asset type provides
    """
    __tablename__ = 'model_detail_template'
    
    # Configuration fields
    asset_type_id = db.Column(db.Integer, db.ForeignKey('asset_types.id'), nullable=True)
    detail_table_type = db.Column(db.String(100), nullable=False)  # e.g., 'emissions_info', 'model_info'
    
    # Relationships
    asset_type = db.relationship('AssetType', backref='model_detail_templates')
    
    def __repr__(self):
        """String representation of the model detail table set"""
        return f'<ModelDetailTableTemplate AssetType:{self.asset_type_id}:{self.detail_table_type}>'
    
    @classmethod
    def get_detail_table_types_for_model(cls, asset_type_id):
        """Get all detail table types configured for a specific model"""
        return cls.query.filter(
            (cls.asset_type_id == asset_type_id) | (cls.asset_type_id == None)
        ).all()
    
    @classmethod
    def get_model_detail_types_for_model(cls, asset_type_id):
        """Get model detail table types configured for a specific model"""
        return cls.query.filter_by(
            asset_type_id=asset_type_id,
        ).all()
    
    @classmethod
    def create_detail_table_rows(cls, model_id, asset_type_id):
        """Create detail table rows based on model configurations"""
        try:
            # Get all detail table configurations for this model
            detail_configs = cls.get_detail_table_types_for_model(asset_type_id)
            
            for config in detail_configs:
                cls._create_single_detail_row(config, model_id)
                
        except Exception as e:
            logger.debug(f"Error creating model detail table rows for model {model_id}: {e}")
        
    
    @classmethod
    def _create_single_detail_row(cls, config, model_id):
        """Create a single detail table row based on configuration"""
        try:
            # Detail table registry mapping
            detail_table_registry = {
                'emissions_info': 'app.models.assets.model_details.emissions_info.EmissionsInfo',
                'model_info': 'app.models.assets.model_details.model_info.ModelInfo'
            }
            
            detail_table_class_path = detail_table_registry.get(config.detail_table_type)
            if not detail_table_class_path:
                # lookup asset type from model
                from app.models.core.make_model import MakeModel
                model = MakeModel.query.get(model_id)
                asset_type_id = model.asset_type_id
                logger.debug(f"No detail tables found for asset type {asset_type_id}")
                return
            
            # Import the detail table class
            module_path, class_name = detail_table_class_path.rsplit('.', 1)
            module = __import__(module_path, fromlist=[class_name])
            detail_table_class = getattr(module, class_name)
            
            existing_row = detail_table_class.query.filter_by(make_model_id=model_id).first()
            if existing_row:
                return  # Already exists, don't create duplicate
            detail_row = detail_table_class(make_model_id=model_id)
            db.session.add(detail_row)

        except Exception as e:
            logger.debug(f"Error creating detail row for {config.detail_table_type}: {e}")
            # Don't rollback here - let the main transaction handle it 