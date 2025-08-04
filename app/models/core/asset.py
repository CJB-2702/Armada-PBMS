from app.models.core.user_created_base import UserCreatedBase
from app import db

class Asset(UserCreatedBase, db.Model):
    __tablename__ = 'assets'
    
    # Class-level state for automatic detail insertion
    _automatic_detail_insertion_enabled = False
    _detail_table_registry = None
    _detail_creation_in_progress = False
    _event_creation_in_progress = False
    
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
        # Also set up post-commit listener as backup
        event.listen(db.session, 'after_commit', cls._create_detail_rows_after_commit)
        
        print("Automatic detail insertion enabled successfully")
    
    @classmethod
    def disable_automatic_detail_insertion(cls):
        """Disable automatic detail table row creation"""
        cls._automatic_detail_insertion_enabled = False
        print("Automatic detail insertion disabled")

    @classmethod
    def _create_detail_rows_after_insert(cls, mapper, connection, target):
        """Event listener for automatic detail row creation and event creation"""
        print(f"DEBUG: Event listener triggered for asset {target.id}")
        if not cls._automatic_detail_insertion_enabled:
            print(f"DEBUG: Automatic detail insertion not enabled")
            return
        
        try:
            print(f"DEBUG: Creating detail table rows for asset {target.id}")
            # Use a separate session to avoid flush conflicts
            from app import create_app
            app = create_app()
            with app.app_context():
                # Re-query the asset to ensure we have a fresh session
                asset = cls.query.get(target.id)
                if asset:
                    print(f"DEBUG: Found asset, creating detail rows")
                    asset._create_detail_table_rows()
                    
                    # Create event for asset creation
                    asset._create_asset_creation_event()
                else:
                    print(f"DEBUG: Asset not found after re-query")
        except Exception as e:
            print(f"Warning: Failed to create detail rows for asset {target.id}: {e}")

    @classmethod
    def _create_detail_rows_after_commit(cls, session):
        """Post-commit event listener for automatic detail row creation"""
        print(f"DEBUG: Post-commit event triggered")
        if not cls._automatic_detail_insertion_enabled or cls._detail_creation_in_progress:
            print(f"DEBUG: Skipping detail creation - already in progress or disabled")
            return
        
        try:
            cls._detail_creation_in_progress = True
            # Use a completely separate session
            from app import create_app
            app = create_app()
            with app.app_context():
                # Get the most recently created asset
                latest_asset = cls.query.order_by(cls.id.desc()).first()
                if latest_asset:
                    print(f"DEBUG: Found latest asset {latest_asset.id} in post-commit, creating detail rows")
                    latest_asset._create_detail_table_rows()
                    
                    # Create event for asset creation
                    latest_asset._create_asset_creation_event()
                    
                    # Commit the session to save the detail rows
                    db.session.commit()
                    print(f"DEBUG: Committed detail rows to database")
        except Exception as e:
            print(f"Warning: Failed to create detail rows in post-commit: {e}")
        finally:
            cls._detail_creation_in_progress = False
    
    def _create_detail_table_rows(self):
        """Create detail table rows based on configurations"""
        print(f"DEBUG: _create_detail_table_rows called for asset {self.id}")
        if not self._automatic_detail_insertion_enabled:
            print(f"DEBUG: Automatic detail insertion not enabled")
            return
        
        try:
            # Import detail table sets (conditional import)
            from app.models.assets.detail_table_sets.asset_type_detail_table_set import AssetTypeDetailTableSet
            from app.models.assets.detail_table_sets.model_detail_table_set import ModelDetailTableSet
            
            # Get asset type ID through the relationship
            asset_type_id = None
            if self.asset_type:
                asset_type_id = self.asset_type.id
                print(f"DEBUG: Asset type ID: {asset_type_id}")
            else:
                print(f"DEBUG: No asset type found")
            
            # Create detail table rows for asset type configurations
            if asset_type_id:
                print(f"DEBUG: Creating asset type detail table rows")
                AssetTypeDetailTableSet.create_detail_table_rows(self.id, self.make_model_id)
            
            # Create detail table rows for model configurations
            if self.make_model_id:
                print(f"DEBUG: Creating model detail table rows")
                ModelDetailTableSet.create_detail_table_rows(self.id, self.make_model_id)
                
        except Exception as e:
            print(f"Error creating detail table rows for asset {self.id}: {e}")
            # Don't raise the exception to prevent asset creation from failing
    
    def _create_asset_creation_event(self):
        """Create an event when an asset is created"""
        # Check if event creation is already in progress to prevent duplicates
        if Asset._event_creation_in_progress:
            print(f"DEBUG: Event creation already in progress for asset {self.id}, skipping")
            return
        
        try:
            Asset._event_creation_in_progress = True
            from app.models.core.event import Event
            
            # Check if event already exists for this asset
            existing_event = Event.query.filter_by(
                event_type='Asset Created',
                asset_id=self.id
            ).first()
            
            if existing_event:
                print(f"DEBUG: Asset creation event already exists for asset {self.id}, skipping")
                return
            
            # Create event description
            description = f"Asset '{self.name}' ({self.serial_number}) was created"
            if self.major_location:
                description += f" at location '{self.major_location.name}'"
            
            # Create the event
            event = Event(
                event_type='Asset Created',
                description=description,
                user_id=self.created_by_id,  # User who created the asset
                asset_id=self.id,  # The asset that was created
                major_location_id=self.major_location_id  # Location of the asset
            )
            
            db.session.add(event)
            db.session.commit()
            
            print(f"DEBUG: Created asset creation event for asset {self.id}")
            
        except Exception as e:
            print(f"Warning: Failed to create asset creation event for asset {self.id}: {e}")
            # Don't raise the exception to prevent asset creation from failing
        finally:
            Asset._event_creation_in_progress = False
    
    def __repr__(self):
        return f'<Asset {self.name} ({self.serial_number})>' 