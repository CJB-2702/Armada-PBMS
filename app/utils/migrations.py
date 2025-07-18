import os
import json
from datetime import datetime
from app.extensions import db
from app.utils.logger import get_logger

logger = get_logger()

class MigrationManager:
    """Manages database migrations and data updates"""
    
    def __init__(self, app):
        self.app = app
        self.migrations_dir = os.path.join(os.path.dirname(__file__), '..', 'models', 'BaseModels', 'initial_data')
        self.migration_history = []
    
    def create_migration_table(self):
        """Create migration history table if it doesn't exist"""
        with self.app.app_context():
            db.session.execute(db.text("""
                CREATE TABLE IF NOT EXISTS migration_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    migration_name VARCHAR(255) NOT NULL,
                    applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    status VARCHAR(50) DEFAULT 'completed',
                    details TEXT
                )
            """))
            db.session.commit()
    
    def get_applied_migrations(self):
        """Get list of applied migrations"""
        with self.app.app_context():
            try:
                result = db.session.execute(db.text("""
                    SELECT migration_name FROM migration_history 
                    WHERE status = 'completed' 
                    ORDER BY applied_at
                """))
                return [row[0] for row in result.fetchall()]
            except Exception as e:
                logger.warning(f"Could not fetch migration history: {e}")
                return []
    
    def record_migration(self, migration_name, status='completed', details=None):
        """Record a migration in the history table"""
        with self.app.app_context():
            try:
                db.session.execute(db.text("""
                    INSERT INTO migration_history (migration_name, status, details)
                    VALUES (:migration_name, :status, :details)
                """), {
                    'migration_name': migration_name,
                    'status': status,
                    'details': details
                })
                db.session.commit()
                logger.info(f"Migration recorded: {migration_name} - {status}")
            except Exception as e:
                logger.error(f"Failed to record migration {migration_name}: {e}")
    
    def migrate_data(self):
        """Run all pending migrations"""
        with self.app.app_context():
            self.create_migration_table()
            applied_migrations = self.get_applied_migrations()
            
            # Define migrations in order
            migrations = [
                ('001_initial_data', self._migrate_001_initial_data),
                ('002_update_event_types', self._migrate_002_update_event_types),
                ('003_add_user_permissions', self._migrate_003_add_user_permissions),
                ('004_fix_users_table_schema', self._migrate_004_fix_users_table_schema),
            ]
            
            for migration_name, migration_func in migrations:
                if migration_name not in applied_migrations:
                    logger.info(f"Running migration: {migration_name}")
                    try:
                        migration_func()
                        self.record_migration(migration_name, 'completed')
                        logger.info(f"Migration completed: {migration_name}")
                    except Exception as e:
                        error_msg = f"Migration {migration_name} failed: {str(e)}"
                        logger.error(error_msg)
                        self.record_migration(migration_name, 'failed', error_msg)
                        raise
                else:
                    logger.info(f"Migration already applied: {migration_name}")
    
    def _migrate_001_initial_data(self):
        """Initial data migration - this is handled by insert_initial_data"""
        logger.info("Initial data migration - using existing insert_initial_data function")
        # This migration is handled by the existing insert_initial_data function
        pass
    
    def _migrate_002_update_event_types(self):
        """Update event types with additional metadata"""
        logger.info("Updating event types with additional metadata")
        
        # Add new event types if they don't exist
        new_event_types = [
            {
                'name': 'Maintenance',
                'description': 'Maintenance and repair events',
                'created_by': 0
            },
            {
                'name': 'Incident',
                'description': 'Incident and emergency events',
                'created_by': 0
            }
        ]
        
        for event_type_data in new_event_types:
            # Check if event type already exists
            existing = db.session.execute(db.text("""
                SELECT row_id FROM types_events WHERE value = :value
            """), {'value': event_type_data['name']}).fetchone()
            
            if not existing:
                # Get next available row_id
                result = db.session.execute(db.text("""
                    SELECT COALESCE(MAX(row_id), -1) + 1 FROM types_events
                """)).fetchone()
                next_id = result[0] if result else 0
                
                db.session.execute(db.text("""
                    INSERT INTO types_events (row_id, value, description, created_by, updated_by, created_at, updated_at)
                    VALUES (:row_id, :value, :description, :created_by, :updated_by, :created_at, :updated_at)
                """), {
                    'row_id': next_id,
                    'value': event_type_data['name'],
                    'description': event_type_data['description'],
                    'created_by': event_type_data['created_by'],
                    'updated_by': event_type_data['created_by'],
                    'created_at': datetime.now(),
                    'updated_at': datetime.now()
                })
        
        db.session.commit()
        logger.info("Event types updated successfully")
    
    def _migrate_003_add_user_permissions(self):
        """Add user permissions table and basic permissions"""
        logger.info("Adding user permissions system")
        
        # Create permissions table
        db.session.execute(db.text("""
            CREATE TABLE IF NOT EXISTS user_permissions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                permission_name VARCHAR(100) NOT NULL,
                granted BOOLEAN DEFAULT TRUE,
                granted_by INTEGER,
                granted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (row_id),
                FOREIGN KEY (granted_by) REFERENCES users (row_id),
                UNIQUE(user_id, permission_name)
            )
        """))
        
        # Add basic permissions for admin users
        admin_users = db.session.execute(db.text("""
            SELECT row_id FROM users WHERE is_admin = 1
        """)).fetchall()
        
        basic_permissions = [
            'events.create',
            'events.edit',
            'events.delete',
            'events.view',
            'event_types.manage',
            'users.manage',
            'assets.manage',
            'locations.manage'
        ]
        
        for admin_user in admin_users:
            user_id = admin_user[0]
            for permission in basic_permissions:
                db.session.execute(db.text("""
                    INSERT OR IGNORE INTO user_permissions (user_id, permission_name, granted, granted_by)
                    VALUES (:user_id, :permission, :granted, :granted_by)
                """), {
                    'user_id': user_id,
                    'permission': permission,
                    'granted': True,
                    'granted_by': 0  # SYSTEM
                })
        
        db.session.commit()
        logger.info("User permissions system added successfully")
    
    def _migrate_004_fix_users_table_schema(self):
        """Add missing columns to the users table to match the model definition"""
        logger.info("Fixing users table schema to match model definition")
        
        # Check which columns exist
        result = db.session.execute(db.text("PRAGMA table_info(users)"))
        existing_columns = [row[1] for row in result.fetchall()]
        
        # Add missing columns if they don't exist
        missing_columns = []
        
        if 'password_hash' not in existing_columns:
            missing_columns.append('password_hash VARCHAR(255)')
        
        if 'is_active' not in existing_columns:
            missing_columns.append('is_active BOOLEAN DEFAULT 1')
        
        if 'last_login' not in existing_columns:
            missing_columns.append('last_login DATETIME')
        
        # Add the missing columns
        for column_def in missing_columns:
            column_name = column_def.split()[0]
            logger.info(f"Adding column: {column_name}")
            db.session.execute(db.text(f"ALTER TABLE users ADD COLUMN {column_def}"))
        
        db.session.commit()
        logger.info(f"Users table schema fixed successfully. Added columns: {[col.split()[0] for col in missing_columns]}")
    
    def rollback_migration(self, migration_name):
        """Rollback a specific migration"""
        logger.warning(f"Rollback functionality not implemented for {migration_name}")
        # This would need to be implemented based on specific migration requirements
        pass
    
    def get_migration_status(self):
        """Get status of all migrations"""
        with self.app.app_context():
            try:
                result = db.session.execute(db.text("""
                    SELECT migration_name, status, applied_at, details 
                    FROM migration_history 
                    ORDER BY applied_at DESC
                """))
                return result.fetchall()
            except Exception as e:
                logger.error(f"Could not fetch migration status: {e}")
                return []

def run_migrations(app):
    """Run all pending migrations"""
    migration_manager = MigrationManager(app)
    migration_manager.migrate_data() 