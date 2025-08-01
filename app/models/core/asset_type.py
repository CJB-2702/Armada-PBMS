from app.models.core.user_created_base import UserCreatedBase
from app import db

class AssetType(UserCreatedBase, db.Model):
    __tablename__ = 'asset_types'
    
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=True)
    category = db.Column(db.String(100), nullable=True)
    is_active = db.Column(db.Boolean, default=True)
    
    # Relationships (no backrefs)
    assets = db.relationship('Asset')
    
    def __repr__(self):
        return f'<AssetType {self.name}>' 