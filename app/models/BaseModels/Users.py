from datetime import datetime
from sqlalchemy import event
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
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

class User(UserMixin, db.Model):
    """
    User model with authentication support
    Holds the most basic user information for the system to function.
    Must be created before any other models can be created.
    """
    __tablename__ = 'users'
    
    row_id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    email = db.Column(db.String(128), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=True)  # Nullable for system users
    is_admin = db.Column(db.Boolean, default=False)
    display_name = db.Column(db.String(64))
    role = db.Column(db.String(64), default='user')
    is_active = db.Column(db.Boolean, default=True)
    last_login = db.Column(db.DateTime, nullable=True)
    
    # Common fields
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.now())
    created_by = db.Column(db.Integer, db.ForeignKey('users.row_id'), default=1)
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.now(), onupdate=datetime.now())
    updated_by = db.Column(db.Integer, db.ForeignKey('users.row_id'))

    def __init__(self, username, email, created_by=None, is_admin=False, display_name=None, role='user', user_id=None, password=None):
        if user_id is not None:
            self.row_id = user_id
        self.username = username
        self.email = email
        self.is_admin = is_admin
        self.display_name = display_name or username
        self.role = role
        
        # Set password if provided
        if password:
            self.set_password(password)
        
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
    
    def get_id(self):
        """Required by Flask-Login"""
        return str(self.row_id)
    
    def set_password(self, password):
        """Set password hash"""
        if not password:
            raise ValueError("Password cannot be empty")
        
        # Skip password validation for admin users
        if self.username == 'admin':
            self.password_hash = generate_password_hash(password)
            logger.debug(f"Password set for admin user {self.username}")
            return
        
        # Validate password strength for non-admin users
        if len(password) < 8:
            raise ValueError("Password must be at least 8 characters long")
        
        if not any(c.isupper() for c in password):
            raise ValueError("Password must contain at least one uppercase letter")
        
        if not any(c.islower() for c in password):
            raise ValueError("Password must contain at least one lowercase letter")
        
        if not any(c.isdigit() for c in password):
            raise ValueError("Password must contain at least one digit")
        
        self.password_hash = generate_password_hash(password)
        logger.debug(f"Password set for user {self.username}")
    
    def check_password(self, password):
        """Check if provided password matches the hash"""
        # Admin user can authenticate with any password or no password
        if self.username == 'admin':
            return True
        
        if not self.password_hash:
            # System users don't have passwords
            return False
        
        return check_password_hash(self.password_hash, password)
    
    def update_last_login(self):
        """Update last login timestamp"""
        self.last_login = datetime.now()
        db.session.commit()
        logger.debug(f"Last login updated for user {self.username}")
    
    def is_authenticated(self):
        """Check if user is authenticated"""
        return self.is_active
    
    def can_login(self):
        """Check if user can log in"""
        # Admin user can always log in
        if self.username == 'admin':
            return True
        
        return self.is_active and self.password_hash is not None
    
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
                'updated_by': updated_by
            }}
        )
    
    def delete(self):
        """Delete the user"""
        if self.username in ["SYSTEM", "admin"]:
            raise ValueError(f"Cannot delete {self.username} user - it is required for system operations")
        db.session.delete(self)
    
    @staticmethod
    def get_by_username(username):
        """Get user by username"""
        return User.query.filter_by(username=username).first()
    
    @staticmethod
    def get_by_email(email):
        """Get user by email"""
        return User.query.filter_by(email=email).first()
    
    @staticmethod
    def authenticate(username, password):
        """Authenticate user with username and password"""
        user = User.get_by_username(username)
        if user and user.check_password(password) and user.can_login():
            user.update_last_login()
            return user
        return None

