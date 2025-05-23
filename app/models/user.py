from app import db, login_manager
from flask_login import UserMixin
import json
from pathlib import Path

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    
    user_id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    display_name = db.Column(db.String(120))
    role = db.Column(db.String(20))
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())

    def get_id(self):
        return str(self.user_id)

    def __repr__(self):
        return f'<User {self.username}>'

    @classmethod
    def load_default_users(cls):
        """Load default users from JSON file if none exist"""
        if cls.query.first() is None:
            current_dir = Path(__file__).parent
            json_path = current_dir / 'default_data' / 'default_users.json'
            
            try:
                data = json.loads(json_path.read_text())
                    
                for user_data in data['users']:
                    user = cls(**user_data)
                    db.session.add(user)
                
                db.session.commit()
                print("Default users loaded successfully!")
            except Exception as e:
                print(f"Error loading default users: {e}")
                db.session.rollback()

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id)) 