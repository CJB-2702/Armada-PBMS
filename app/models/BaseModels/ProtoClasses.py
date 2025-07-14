from datetime import datetime
from app.extensions import db
from app.utils.logger import get_logger

logger = get_logger()

class UserCreated(db.Model):

    """Base model class that contains common fields for all models"""
    __abstract__ = True  # This makes SQLAlchemy not create a table for this model
    
    # Common fields
    row_id = db.Column(db.Integer, primary_key=True)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.now())
    created_by = db.Column(db.Integer, db.ForeignKey('users.row_id'))
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.now(), onupdate=datetime.now())
    updated_by = db.Column(db.Integer, db.ForeignKey('users.row_id'))
    
    def __init__(self, created_by=None, **kwargs):
        """Initialize base model with common fields"""
        if created_by is not None:
            self.created_by = created_by
            self.updated_by = created_by  # Set to same as created_by initially
        
        # Set any additional kwargs as attributes
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
    
    def update(self, updated_by, **kwargs):
        """Update model with new values and log the change"""
        old_values = {key: getattr(self, key) for key in kwargs.keys() if hasattr(self, key)}
        
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
        
        self.updated_at = datetime.now()
        self.updated_by = updated_by
        
        # Log the update
        logger.info(
            f'{self.__class__.__name__} Updated: {getattr(self, "common_name", getattr(self, "name", "Unknown"))}',
            extra={'log_data': {
                'model_id': getattr(self, f'{self.__class__.__name__.lower()}_row_id', None),
                'old_values': old_values,
                'new_values': kwargs,
                'user_id': updated_by
            }}
        )
        
class Types(UserCreated):
    """Base class for type/category tables
    
    Known child classes:
    - AssetTypes (app.models.BaseModels.Asset)
    - EventTypes (app.models.BaseModels.Event)
    """
    __abstract__ = True
    value = db.Column(db.String(64), nullable=False, unique=True)
    description = db.Column(db.Text)
    
    def can_be_deleted(self):
        """Check if this type can be deleted based on hardcoded logic
        
        Returns:
            bool: True if the type can be deleted, False if it's a protected base type
        """
        # Get the protected base types for this specific type class
        protected_types = self.get_protected_types()
        
        # Check if this type's value is in the protected list
        return self.value not in protected_types
    
    def get_protected_types(self):
        """Get the list of protected types that cannot be deleted
        
        This method should be overridden by child classes to specify their protected types.
        
        Returns:
            list: List of type values that are protected from deletion
        """
        # Default implementation - child classes should override this
        return []
    
    def delete(self):
        """Override delete method to prevent deletion of protected types"""
        if not self.can_be_deleted():
            raise ValueError(f"Cannot delete protected type '{self.value}'. This is a system-required type.")
        # If we get here, the type can be deleted, so proceed with normal deletion
        db.session.delete(self)
        db.session.commit()
        return True

class GroupedLists(Types):
    __abstract__ = True
    UID = db.Column(db.String(100), unique=True)
    group = db.Column(db.String(100), nullable=False)

    def __init__(self, group, value, description, created_by=0):
        super().__init__(created_by)
        uid = f"{group}_{value}"
        self.group = group
        self.value = value
        self.description = description
        self.UID = uid