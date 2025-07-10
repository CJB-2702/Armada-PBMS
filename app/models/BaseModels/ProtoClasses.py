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
    created_by = db.Column(db.Integer, db.ForeignKey('users.row_id'), nullable=True)
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.now(), onupdate=datetime.now())
    updated_by = db.Column(db.Integer, db.ForeignKey('users.row_id'), nullable=True)
    
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
    __abstract__ = True
    value = db.Column(db.String(64), nullable=False, unique=True)
    description = db.Column(db.Text)
    deletable = db.Column(db.Boolean, default=True)