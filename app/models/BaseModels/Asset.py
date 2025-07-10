from datetime import datetime
from app.extensions import db
from app.utils.logger import get_logger
from app.models.BaseModels.ProtoClasses import UserCreated, Types

logger = get_logger()

initial_asset_types = [
    {
        "name": "System",
        "description": "System assets",
        "created_by": 0
    },
    {
        "name": "General",
        "description": "General assets",
        "created_by": 0
    }
]

class AssetTypes(Types):
    __tablename__ = 'types_assets'


class Asset(UserCreated):
    __tablename__ = 'asset'
    __abstract__ = True  # Make this an abstract base class

    UID = db.Column(db.String(50), nullable=False, unique=True)
    asset_type = db.Column(db.String(50), db.ForeignKey('types_assets.value'), default='General')
    common_name = db.Column(db.String(100))
    description = db.Column(db.Text, nullable=False)
    status = db.Column(db.String(50), default='active')
    
    # Foreign key relationships that apply to all asset types
    parent_asset_id = db.Column(db.Integer, db.ForeignKey('MajorLocations.row_id'), nullable=True)
    assigned_user_id = db.Column(db.Integer, db.ForeignKey('users.row_id'), nullable=True)
    last_event_id = db.Column(db.Integer, db.ForeignKey('events.row_id'), nullable=True)

    def __init__(self, UID, asset_type, common_name, description, status, created_by=0):
        self.UID = UID
        self.asset_type = asset_type
        self.common_name = common_name
        self.description = description
        self.status = status
        self.created_by = created_by
        self.updated_by = created_by


def ensure_required_asset_types():
    """Ensure required asset types exist in the database"""
    logger.info("Starting Asset Types initialization...")
    logger.info(f"Required asset types to create: {len(initial_asset_types)}")
    
    for asset_data in initial_asset_types:
        try:
            logger.info(f"Checking for asset type: {asset_data['name']}")
            existing_type = AssetTypes.query.filter_by(value=asset_data['name']).first()
            if not existing_type:
                logger.info(f"Creating asset type: {asset_data['name']}")
                asset_type = AssetTypes(
                    value=asset_data['name'],
                    description=asset_data['description'],
                    created_by=asset_data['created_by']
                )
                db.session.add(asset_type)
                logger.info(f"✓ Created required asset type: {asset_data['name']}")
            else:
                logger.info(f"✓ Asset type already exists: {asset_data['name']}")
        except Exception as e:
            logger.error(f"Error creating asset type {asset_data['name']}: {e}")
            continue
    
    try:
        db.session.commit()
        logger.info("✓ Asset types database commit successful")
    except Exception as e:
        logger.error(f"Error committing asset types to database: {e}")
        db.session.rollback()
        raise
    
    # Verify final count
    final_count = AssetTypes.query.count()
    logger.info(f"Final asset type count: {final_count}")
    logger.info("✓ Required asset types check completed")