from app.models.core.user_created_base import UserCreatedBase
from app.logger import get_logger
logger = get_logger("asset_management.models.core")
from app import db
from sqlalchemy import event

class Asset(UserCreatedBase, db.Model):
    __tablename__ = 'assets'
    
    # Class-level state for automatic detail insertion
    _automatic_detail_insertion_enabled = True  # Always enabled by default
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
    def asset_type(self):
        """Get the asset type through the make_model relationship"""
        if self.make_model and self.make_model.asset_type:
            return self.make_model.asset_type
        return None
    
    @classmethod
    def enable_automatic_detail_insertion(cls):
        """Enable automatic detail table row creation for new assets"""
        if cls._automatic_detail_insertion_enabled:
            return
        cls._automatic_detail_insertion_enabled = True
        logger.debug("Automatic detail insertion enabled")
    
    @classmethod
    def disable_automatic_detail_insertion(cls):
        """Disable automatic detail table row creation"""
        cls._automatic_detail_insertion_enabled = False

    @classmethod
    def _after_insert(cls, mapper, connection, target):
        """Handle all post-insert events for an asset"""
        if not cls._automatic_detail_insertion_enabled:
            return
        
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
    
    def create_detail_table_rows(self):
        """Create detail table rows for this asset after it has been committed"""
        if not self._automatic_detail_insertion_enabled:
            return
        
        try:
            from app.models.assets.detail_table_sets.asset_type_detail_table_set import AssetTypeDetailTableSet
            from app.models.assets.detail_table_sets.model_detail_table_set import ModelDetailTableSet
            
            if self.asset_type:
                AssetTypeDetailTableSet.create_detail_table_rows(self.id, self.make_model_id)
            
            if self.make_model_id:
                ModelDetailTableSet.create_detail_table_rows(self.id, self.make_model_id)
                
        except Exception as e:
            logger.debug(f"Error creating detail table rows for asset {self.id}: {e}")
    
    def __repr__(self):
        return f'<Asset {self.name} ({self.serial_number})>' 

# Enable the after_insert listener by default when the class is loaded
event.listen(Asset, 'after_insert', Asset._after_insert) 