from app.models.core.user_created_base import UserCreatedBase
from app import db

class MakeModel(UserCreatedBase, db.Model):
    __tablename__ = 'make_models'
    
    make = db.Column(db.String(100), nullable=False)
    model = db.Column(db.String(100), nullable=False)
    year = db.Column(db.Integer, nullable=True)
    revision = db.Column(db.String(100), nullable=True)
    description = db.Column(db.Text, nullable=True)
    is_active = db.Column(db.Boolean, default=True)
    asset_type_id = db.Column(db.Integer, db.ForeignKey('asset_types.id'), nullable=True)
    meter1_unit = db.Column(db.String(100), nullable=True)
    meter2_unit = db.Column(db.String(100), nullable=True)
    meter3_unit = db.Column(db.String(100), nullable=True)
    meter4_unit = db.Column(db.String(100), nullable=True)

    
    # Relationships (no backrefs)
    assets = db.relationship('Asset')
    asset_type = db.relationship('AssetType')
    
    def __repr__(self):
        return f'<MakeModel {self.make} {self.model}>' 