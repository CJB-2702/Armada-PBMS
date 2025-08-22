from app.models.core.user_created_base import UserCreatedBase
from app import db
from app.logger import get_logger
logger = get_logger("asset_management.models.core")
from sqlalchemy import event

class MakeModel(UserCreatedBase):
    __tablename__ = 'make_models'
    _automatic_detail_insertion_enabled = True
    
    make = db.Column(db.String(100), nullable=False)
    model = db.Column(db.String(100), nullable=False)
    year = db.Column(db.Integer, nullable=True)
    revision = db.Column(db.String(100), nullable=True)
    description = db.Column(db.Text, nullable=True)
    is_active = db.Column(db.Boolean, default=True)
    asset_type_id = db.Column(db.Integer, db.ForeignKey('asset_types.id'), nullable=True)
    meter1_unit = db.Column(db.String(100), nullable=True)
    meter2_unit = db.Column(db.String(100), nullable=True)
    meter3_unit = db.Column(db.String(100), nullable=True)
    meter4_unit = db.Column(db.String(100), nullable=True)

    
    # Relationships (no backrefs)
    assets = db.relationship('Asset')
    asset_type = db.relationship('AssetType')
    
    def __repr__(self):
        return f'<MakeModel {self.make} {self.model}>' 

    @classmethod
    def enable_automatic_detail_insertion(cls):
        """Enable automatic detail table row creation for new models"""
        cls._automatic_detail_insertion_enabled = True
        logger.debug("Automatic detail insertion enabled")
    
    @classmethod
    def disable_automatic_detail_insertion(cls):
        """Disable automatic detail table row creation"""
        cls._automatic_detail_insertion_enabled = False

    @classmethod
    def _after_insert(cls, mapper, connection, target):
        """Handle all post-insert events for a model"""
        try:
            # Create model creation event
            from app.models.core.event import Event
            event = Event(
                event_type='Model Created',
                description=f"Model '{target.make} {target.model}' ({target.year}) was created",
                user_id=target.created_by_id,
            )
            db.session.add(event)
            
        except Exception as e:
            logger.debug(f"Error in post-insert events: {e}")

        if cls._automatic_detail_insertion_enabled:
            target.create_detail_table_rows()
    
    def create_detail_table_rows(self):
        """Create detail table rows for this model after it has been committed"""
        if not self._automatic_detail_insertion_enabled:
            return
        
        try:
            from app.models.assets.detail_table_templates.model_detail_table_template import ModelDetailTableTemplate
            ModelDetailTableTemplate.create_detail_table_rows(self.id, self.asset_type_id)
        except Exception as e:
            logger.debug(f"Error creating detail table rows for model {self.id}: {e}")

# Enable the after_insert listener by default when the class is loaded
event.listen(MakeModel, 'after_insert', MakeModel._after_insert) 