from app import db

class AssetType(db.Model):
    __tablename__ = 'asset_types'
    
    type_id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(10), unique=True, nullable=False)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    category = db.Column(db.String(50))  # For grouping (e.g., 'Vehicle', 'Equipment')
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())

    def to_dict(self):
        return {
            'type_id': self.type_id,
            'code': self.code,
            'name': self.name,
            'description': self.description,
            'category': self.category
        }

    def __repr__(self):
        return f'<AssetType {self.code}: {self.name}>' 