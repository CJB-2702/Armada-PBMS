from app import db, login_manager
from flask_login import UserMixin
import json
from pathlib import Path
from app.utils.event_logger import log_event
from sqlalchemy import event
from app.models.event import Event

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    
    user_id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    display_name = db.Column(db.String(120))
    role = db.Column(db.String(20), nullable=False)
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())

    def get_id(self):
        return str(self.user_id)

    def __repr__(self):
        return f'<User {self.username}>'

@event.listens_for(User, 'after_insert')
def create_user_event(mapper, connection, target):
    connection.execute(
        Event.__table__.insert(),
        {
            'event_type': 'user_created',
            'title': 'New User Created',
            'description': f'User {target.username} was added to the system',
            'created_by': 1,
            'user_id': target.user_id
        }
    )

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id)) 