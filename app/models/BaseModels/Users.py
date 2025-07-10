from datetime import datetime
from sqlalchemy import event
from app.extensions import db
from app.utils.logger import get_logger


logger = get_logger()

Required_users = [
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
    """Perfect! Now let's test the implementation to see if the event listener works correctly:
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
    updated_by = db.Column(db.Integer, db.ForeignKey('users.row_id'), nullable=True)

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


@event.listens_for(User.__table__, 'after_create')
def insert_initial_users(target, connection, **kw):
    """Automatically insert required users when the User table is created"""
    logger.info("=== Auto-creating required users ===")
    
    # Check if users already exist to avoid duplicates
    try:
        # Use raw SQL to check if users exist (since the model might not be fully initialized yet)
        result = connection.execute(db.text("SELECT COUNT(*) FROM users"))
        existing_count = result.scalar()
        
        if existing_count > 0:
            logger.info(f"Users table already has {existing_count} users, skipping initial user creation")
            return
            
    except Exception as e:
        logger.warning(f"Could not check existing users: {e}")
    
    # Insert required users
    for user_data in Required_users:
        try:
            logger.info(f"Creating required user: {user_data['username']}")
            
            # Use raw SQL to insert with specific row_id
            connection.execute(db.text("""
                INSERT INTO users (row_id, username, email, is_admin, display_name, role, created_by, updated_by, created_at, updated_at)
                VALUES (:row_id, :username, :email, :is_admin, :display_name, :role, :created_by, :updated_by, :created_at, :updated_at)
            """), {
                'row_id': user_data['row_id'],
                'username': user_data['username'],
                'email': user_data['email'],
                'is_admin': user_data['is_admin'],
                'display_name': user_data['display_name'],
                'role': user_data['role'],
                'created_by': user_data['created_by'],
                'updated_by': user_data['created_by'],  # Same as created_by initially
                'created_at': datetime.now(),
                'updated_at': datetime.now()
            })
            
            logger.info(f"✓ Created required user: {user_data['username']} (ID: {user_data['row_id']})")
            
        except Exception as e:
            logger.error(f"Error creating user {user_data['username']}: {e}")
            # Don't raise here - let the table creation complete even if user creation fails
    
    logger.info("=== Required users auto-creation completed ===")

