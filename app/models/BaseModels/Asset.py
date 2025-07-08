from datetime import datetime
from app import db
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

    def __init__(self, value, description, created_by=None):
        super().__init__(value, description, created_by)


class Asset(UserCreated):
    __tablename__ = 'asset'

    UID = db.Column(db.String(50), nullable=False, unique=True)
    asset_type = db.Column(db.String(50), db.ForeignKey('types_assets.value'), default='General')
    common_name = db.Column(db.String(100))
    description = db.Column(db.Text, nullable=False)
    status = db.Column(db.String(50), default='active')

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
    try:
        AssetTypes.query.first()
        for asset_data in initial_asset_types:
            existing_type = AssetTypes.query.filter_by(value=asset_data['name']).first()
            if not existing_type:
                asset_type = AssetTypes(
                    value=asset_data['name'],
                    description=asset_data['description'],
                    created_by=asset_data['created_by']
                )
                db.session.add(asset_type)
                logger.info(f"Created required asset type: {asset_data['name']}")
        db.session.commit()
        logger.info("Required asset types check completed")
    except Exception as e:
        logger.debug(f"Asset types table not ready yet: {e}")
        pass