from datetime import datetime
from sqlalchemy import event
from app.extensions import db
from app.utils.logger import get_logger


logger = get_logger()

required_users = [
            {
                "row_id": 0,
                "username": "SYSTEM",
                "email": "system@null.null",
                "is_admin": True,
                "display_name": "System",
                "role": "admin",
                "created_by": 0,
            },
            {
                "row_id": 1,
                "username": "admin",
                "email": "admin@null.com",
                "is_admin": True,
                "display_name": "System Administrator",
                "role": "admin",
                "created_by": 0,
            }
        ]

class User(db.Model):
    """
    User model
    Holds the most basic user information for the system to function.
    Must be created before any other models can be created.
    """
    __tablename__ = 'users'
    
    row_id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    email = db.Column(db.String(128), unique=True, nullable=False)
    is_admin = db.Column(db.Boolean, default=False)
    display_name = db.Column(db.String(64))
    role = db.Column(db.String(64), default='user')
    
    # Common fields
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.now())
    created_by = db.Column(db.Integer, db.ForeignKey('users.row_id'), default=1)
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.now(), onupdate=datetime.now())
    updated_by = db.Column(db.Integer, db.ForeignKey('users.row_id'))

    def __init__(self, username, email, created_by=None, is_admin=False, display_name=None, role='user', user_id=None):
        if user_id is not None:
            self.row_id = user_id
        self.username = username
        self.email = email
        self.is_admin = is_admin
        self.display_name = display_name or username
        self.role = role
        if created_by is not None:
            self.created_by = created_by
            self.updated_by = created_by
        
        logger.debug(
            'Creating user',
            extra={'log_data': {
                'username': username,
                'email': email,
                'is_admin': is_admin,
                'created_by': created_by
            }}
        )
    
    def __repr__(self):
        return f'<User {self.username}>'
    
    def update(self, updated_by, **kwargs):
        """Update user with new values and log the change"""
        if self.username in ["SYSTEM", "admin"]:
            raise ValueError(f"Cannot modify {self.username} user - it is required for system operations")
            
        old_values = {key: getattr(self, key) for key in kwargs.keys() if hasattr(self, key)}
        
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
        
        self.updated_at = datetime.now()
        self.updated_by = updated_by
        
        logger.debug(
            'Updating user',
            extra={'log_data': {
                'user_id': self.row_id,
                'old_values': old_values,
                'new_values': kwargs,
                'user_id': updated_by
            }}
        )
    
    def set_password(self, password):
        pass
    
    def check_password(self, password):
        return True
        
    def check_password_hash(self, hash):
        return True

    def delete(self):
        """Delete the user"""
        if self.username in ["SYSTEM", "admin"]:
            raise ValueError(f"Cannot delete {self.username} user - it is required for system operations")
        db.session.delete(self)

