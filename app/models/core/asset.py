from app.models.core.user_created_base import UserCreatedBase
from app.logger import get_logger
logger = get_logger("asset_management.models.core")
from app import db
from sqlalchemy import event

class Asset(UserCreatedBase, db.Model):
    __tablename__ = 'assets'
    
    # Class-level state for automatic detail insertion
    _automatic_detail_insertion_enabled = True
    _detail_table_registry = None
    _detail_rows_created = False  
    
    name = db.Column(db.String(100), nullable=False)
    serial_number = db.Column(db.String(100), unique=True, nullable=False)
    status = db.Column(db.String(50), default='Active')
    major_location_id = db.Column(db.Integer, db.ForeignKey('major_locations.id'), nullable=True)
    make_model_id = db.Column(db.Integer, db.ForeignKey('make_models.id'))
    meter1 = db.Column(db.Float, nullable=True)
    meter2 = db.Column(db.Float, nullable=True)
    meter3 = db.Column(db.Float, nullable=True)
    meter4 = db.Column(db.Float, nullable=True)
    tags = db.Column(db.JSON, nullable=True) # try not to use this if at all possible, left because sometimes users find a good reason.
    detail_rows_created = db.Column(db.JSON, nullable=True) 
    # Relationships
    major_location = db.relationship('MajorLocation', overlaps="assets")
    make_model = db.relationship('MakeModel', overlaps="assets")
    events = db.relationship('Event', backref='asset_ref', lazy='dynamic')


    
    @property
    def asset_type_id(self):
        """Get the asset type ID through the make_model relationship"""
        if self.make_model_id:
            # Use direct query to avoid relationship loading issues in event listeners
            # Do NOT CHANGE THIS. this was a nightmare to fix.
            from app.models.core.make_model import MakeModel
            make_model = MakeModel.query.get(self.make_model_id)
            if make_model:
                return make_model.asset_type_id
        return None
    
    
    def get_asset_type_id(self, force_reload=False):
        """Get the asset type ID with optional force reload for event listener contexts"""
        if force_reload or not hasattr(self, '_cached_asset_type_id'):
            if self.make_model_id:
                from app.models.core.make_model import MakeModel
                make_model = MakeModel.query.get(self.make_model_id)
                self._cached_asset_type_id = make_model.asset_type_id if make_model else None
            else:
                self._cached_asset_type_id = None
        return self._cached_asset_type_id
    
    @classmethod
    def enable_automatic_detail_insertion(cls):
        """Enable automatic detail table row creation for new assets"""
        cls._automatic_detail_insertion_enabled = True
        logger.debug("Automatic detail insertion enabled")
    
    @classmethod
    def disable_automatic_detail_insertion(cls):
        """Disable automatic detail table row creation"""
        cls._automatic_detail_insertion_enabled = False

    @classmethod
    def _after_insert(cls, mapper, connection, target):
        """Handle all post-insert events for an asset"""
        try:
            # Create asset creation event
            from app.models.core.event import Event
            event = Event(
                event_type='Asset Created',
                description=f"Asset '{target.name}' ({target.serial_number}) was created",
                user_id=target.created_by_id,
                asset_id=target.id,
                major_location_id=target.major_location_id
            )
            db.session.add(event)
            
        except Exception as e:
            logger.debug(f"Error in post-insert events: {e}")

        if cls._automatic_detail_insertion_enabled:
            target.create_detail_table_rows()


    
    def create_detail_table_rows(self):
        """Create detail table rows for this asset after it has been committed"""
        logger.info(f"DEBUG: Creating detail table rows for asset {self.id} \n\n\n\n")
        
        
        try:
            from app.models.assets.detail_table_templates.asset_details_from_asset_type import AssetDetailTemplateByAssetType
            from app.models.assets.detail_table_templates.asset_details_from_model_type import AssetDetailTemplateByModelType
            
            # Create asset detail rows based on asset type - use method for reliability in event listeners
            asset_type_id = self.get_asset_type_id(force_reload=True)
            logger.debug(f"DEBUG: Creating asset type detail rows base off of asset type: {asset_type_id} \n\n\n\n")
            if asset_type_id:
                AssetDetailTemplateByAssetType.create_detail_table_rows(self)
            
            # Create asset detail rows based on model type
            if self.make_model_id:
                AssetDetailTemplateByModelType.create_detail_table_rows(self)
                
        except Exception as e:
            logger.debug(f"Error creating detail table rows for asset {self.id}: {e}")

    @classmethod
    def _create_detail_tables_for_asset(cls, asset):
        """Create detail table rows for a specific asset"""
        logger.warning(f"DEBUG: _create_detail_tables_for_asset called for asset {asset.id}")
        try:
            from app.models.assets.detail_table_templates.asset_details_from_asset_type import AssetDetailTemplateByAssetType
            from app.models.assets.detail_table_templates.asset_details_from_model_type import AssetDetailTemplateByModelType
            
            # Create asset detail rows based on asset type - use method for reliability
            asset_type_id = asset.get_asset_type_id(force_reload=True)
            if asset_type_id:
                AssetDetailTemplateByAssetType.create_detail_table_rows(asset)
            else:
                logger.warning(f"DEBUG: No asset type found for asset {asset.id}")
            
            # Create asset detail rows based on model type
            if asset.make_model_id:
                AssetDetailTemplateByModelType.create_detail_table_rows(asset)
                
        except Exception as e:
            logger.debug(f"Error creating detail table rows for asset {asset.id}: {e}")
    
    def __repr__(self):
        return f'<Asset {self.name} ({self.serial_number})>' 

# Enable the after_insert listener by default when the class is loaded
event.listen(Asset, 'after_insert', Asset._after_insert) 