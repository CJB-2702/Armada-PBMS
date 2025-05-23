from app import db
import json
from pathlib import Path

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

    @classmethod
    def load_default_types(cls):
        """Load default asset types from JSON file if none exist"""
        if cls.query.first() is None:
            # Get the path to the JSON file
            current_dir = Path(__file__).parent
            json_path = current_dir / 'default_data' / 'FHWA_asset_types.json'
            
            try:
                data = json.loads(json_path.read_text())
                    
                for type_data in data['asset_types']:
                    asset_type = cls(**type_data)
                    db.session.add(asset_type)
                
                db.session.commit()
                print("Default asset types loaded successfully!")
            except Exception as e:
                print(f"Error loading default asset types: {e}")
                db.session.rollback() 