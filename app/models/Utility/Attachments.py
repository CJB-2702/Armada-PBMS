from app.extensions import db
from app.models.BaseModels.ProtoClasses import UserCreated

class Attachments(UserCreated):
    __tablename__ = 'attachments'

    event_id = db.Column(db.Integer, db.ForeignKey('events.row_id'), nullable=False)
    file_path = db.Column(db.String(100), nullable=False, unique=True)
    file_name = db.Column(db.String(100), nullable=False)
    file_type = db.Column(db.String(100), nullable=False)
    file_size = db.Column(db.Integer, nullable=True)
    file_hash = db.Column(db.String(100), nullable=False)
    tags = db.Column(db.String(100))

    def __init__(self, UID, file_name, file_path, file_type, file_size, file_hash, parent_table, parent_row_id, created_by=0):
        super().__init__(created_by)
        self.file_name = file_name
        self.file_path = file_path
        self.file_type = file_type
