from app.models.core.user_created_base import UserCreatedBase
from app import db

class MakeModel(UserCreatedBase, db.Model):
    __tablename__ = 'make_models'
    
    make = db.Column(db.String(100), nullable=False)
    model = db.Column(db.String(100), nullable=False)
    year = db.Column(db.Integer, nullable=True)
    description = db.Column(db.Text, nullable=True)
    is_active = db.Column(db.Boolean, default=True)
    
    # Relationships (no backrefs)
    assets = db.relationship('Asset')
    
    def __repr__(self):
        return f'<MakeModel {self.make} {self.model}>' 