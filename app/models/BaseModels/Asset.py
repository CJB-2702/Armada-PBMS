from datetime import datetime
from app.extensions import db
from app.utils.logger import get_logger
from app.models.BaseModels.ProtoClasses import UserCreated, Types

logger = get_logger()

required_asset_types = [
    {
        "row_id": 0,
        "name": "System",
        "description": "System assets",
        "created_by": 0
    },
    {
        "row_id": 1,
        "name": "General",
        "description": "General assets",
        "created_by": 0
    },
    {
        "row_id": 2,
        "name": "MajorLocation",
        "description": "Major location assets",
        "created_by": 0
    },
    {
        "row_id": 3,
        "name": "MinorLocation",
        "description": "Minor location assets",
        "created_by": 0
    },
    {
        "row_id": 4,
        "name": "MiscLocation",
        "description": "Miscellaneous location assets",
        "created_by": 0
    }
]

required_statuses = [
    {
        "row_id": 0,
        "name": "Active",
        "description": "Active and in use",
        "created_by": 0
    },
    {
        "row_id": 1,
        "name": "Available",
        "description": "Available and ready to be used",
        "created_by": 0
    },
    {
        "row_id": 2,
        "name": "Unavailable",
        "description": "Unavailable",
        "created_by": 0
    },
    {
        "row_id": 3,
        "name": "Defunct",
        "description": "Something that used to exist, but is now gone",
        "created_by": 0
    }
]

class AssetTypes(Types):
    __tablename__ = 'types_assets'
    
    def get_protected_types(self):
        """Get the list of protected asset types that cannot be deleted
        
        Returns:
            list: List of asset type values that are protected from deletion
        """
        return ['System', 'General', 'MajorLocation', 'MinorLocation', 'MiscLocation']

class Statuses(Types):
    __tablename__ = 'types_statuses'

    def get_protected_types(self):
        """Get the list of protected statuses that cannot be deleted
        
        Returns:
            list: List of status values that are protected from deletion
        """
        return ['Active', 'Available', 'Unavailable', 'Defunct']

class AbstractAsset(UserCreated):
    __abstract__ = True  # Make this an abstract base class

    UID = db.Column(db.String(50), nullable=False, unique=True)
    asset_type = db.Column(db.String(50), db.ForeignKey('types_assets.value'), default='General')
    common_name = db.Column(db.String(100))
    description = db.Column(db.Text, nullable=False)
    status = db.Column(db.String(50), db.ForeignKey('types_statuses.value'), default='Available')
    

    def __init__(self, UID, asset_type, common_name, description, status, created_by=0):
        self.UID = UID
        self.asset_type = asset_type
        self.common_name = common_name
        self.description = description
        self.status = status
        self.created_by = created_by
        self.updated_by = created_by

