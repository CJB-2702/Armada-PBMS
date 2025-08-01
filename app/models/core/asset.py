from app.models.core.user_created_base import UserCreatedBase
from app import db

class Asset(UserCreatedBase, db.Model):
    __tablename__ = 'assets'
    
    # Class-level state for automatic detail insertion
    _automatic_detail_insertion_enabled = False
    _detail_table_registry = None
    
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
    
    # Relationships
    major_location = db.relationship('MajorLocation', overlaps="assets")
    make_model = db.relationship('MakeModel', overlaps="assets")
    
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
            print("Automatic detail insertion already enabled")
            return
        
        print("Enabling automatic detail insertion...")
        
        # Import detail table sets
        from app.models.assets.detail_table_sets.asset_type_detail_table_set import AssetTypeDetailTableSet
        from app.models.assets.detail_table_sets.model_detail_table_set import ModelDetailTableSet
        
        # Enable functionality
        cls._automatic_detail_insertion_enabled = True
        
        # Set up event listener
        from sqlalchemy import event
        event.listen(cls, 'after_insert', cls._create_detail_rows_after_insert)
        
        print("Automatic detail insertion enabled successfully")
    
    @classmethod
    def disable_automatic_detail_insertion(cls):
        """Disable automatic detail table row creation"""
        cls._automatic_detail_insertion_enabled = False
        print("Automatic detail insertion disabled")

    @classmethod
    def _create_detail_rows_after_insert(cls, mapper, connection, target):
        """Event listener for automatic detail row creation"""
        if not cls._automatic_detail_insertion_enabled:
            return
        
        try:
            target._create_detail_table_rows()
        except Exception as e:
            print(f"Warning: Failed to create detail rows for asset {target.id}: {e}")

    
    def _create_detail_table_rows(self):
        """Create detail table rows based on configurations"""
        if not self._automatic_detail_insertion_enabled:
            return
        
        try:
            # Import detail table sets (conditional import)
            from app.models.assets.detail_table_sets.asset_type_detail_table_set import AssetTypeDetailTableSet
            from app.models.assets.detail_table_sets.model_detail_table_set import ModelDetailTableSet
            
            # Get asset type ID through the relationship
            asset_type_id = None
            if self.asset_type:
                asset_type_id = self.asset_type.id
            
            # Create detail table rows for asset type configurations
            if asset_type_id:
                AssetTypeDetailTableSet.create_detail_table_rows(self.id, self.make_model_id)
            
            # Create detail table rows for model configurations
            if self.make_model_id:
                ModelDetailTableSet.create_detail_table_rows(self.id, self.make_model_id)
                
        except Exception as e:
            print(f"Error creating detail table rows for asset {self.id}: {e}")
            # Don't raise the exception to prevent asset creation from failing
    
    def __repr__(self):
        return f'<Asset {self.name} ({self.serial_number})>' 