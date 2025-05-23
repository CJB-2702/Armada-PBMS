from app import db
from datetime import datetime
import json
from pathlib import Path

class Location(db.Model):
    __tablename__ = 'locations'
    
    location_id = db.Column(db.Integer, primary_key=True)
    unique_name = db.Column(db.String(50), unique=True, nullable=False)
    common_name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    country = db.Column(db.String(50))
    state = db.Column(db.String(50))
    city = db.Column(db.String(50))
    street = db.Column(db.String(100))
    building_number = db.Column(db.String(20))
    room = db.Column(db.String(50))
    x = db.Column(db.Float)
    y = db.Column(db.Float)
    z = db.Column(db.Float)
    bin = db.Column(db.String(50))
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())
    updated_at = db.Column(db.DateTime, default=db.func.current_timestamp(), onupdate=db.func.current_timestamp())

    def to_dict(self):
        return {
            'location_id': self.location_id,
            'unique_name': self.unique_name,
            'common_name': self.common_name,
            'description': self.description,
            'country': self.country,
            'state': self.state,
            'city': self.city,
            'street': self.street,
            'building_number': self.building_number,
            'room': self.room,
            'x': self.x,
            'y': self.y,
            'z': self.z,
            'bin': self.bin,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

    def __repr__(self):
        return f'<Location {self.unique_name}>'

    @classmethod
    def load_default_locations(cls):
        """Load default locations from JSON file if none exist"""
        if cls.query.first() is None:
            current_dir = Path(__file__).parent
            json_path = current_dir / 'default_data' / 'default_locations.json'
            
            try:
                data = json.loads(json_path.read_text())
                    
                for loc_data in data['locations']:
                    location = cls(**loc_data)
                    db.session.add(location)
                
                db.session.commit()
                print("Default locations loaded successfully!")
            except Exception as e:
                print(f"Error loading default locations: {e}")
                db.session.rollback() 