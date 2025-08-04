from app.models.core.user_created_base import UserCreatedBase
from app import db
from datetime import datetime
import os
import uuid
from werkzeug.utils import secure_filename
from pathlib import Path

class Attachment(UserCreatedBase, db.Model):
    __tablename__ = 'attachments'
    
    # File information
    filename = db.Column(db.String(255), nullable=False)
    file_size = db.Column(db.Integer, nullable=False)  # Size in bytes
    mime_type = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=True)
    tags = db.Column(db.JSON, nullable=True)  # For categorization
    
    # Storage information
    storage_type = db.Column(db.String(20), nullable=False, default='database')  # 'database' or 'filesystem'
    file_path = db.Column(db.String(500), nullable=True)  # Path for filesystem storage
    file_data = db.Column(db.LargeBinary, nullable=True)  # BLOB for database storage
    
    # Constants
    STORAGE_THRESHOLD = 1024 * 1024  # 1MB threshold
    MAX_FILE_SIZE = 100 * 1024 * 1024  # 100MB max file size
    
    # Allowed file extensions
    ALLOWED_EXTENSIONS = {
        'images': {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp', '.svg'},
        'documents': {'.pdf', '.doc', '.docx', '.xls', '.xlsx', '.ppt', '.pptx', '.txt', '.rtf'},
        'archives': {'.zip', '.rar', '.7z', '.tar', '.gz'},
        'data': {'.csv', '.json', '.xml', '.sql'}
    }
    
    @classmethod
    def get_allowed_extensions(cls):
        """Get all allowed file extensions"""
        all_extensions = set()
        for category in cls.ALLOWED_EXTENSIONS.values():
            all_extensions.update(category)
        return all_extensions
    
    @classmethod
    def is_allowed_file(cls, filename):
        """Check if file extension is allowed"""
        if not filename:
            return False
        
        file_ext = Path(filename).suffix.lower()
        return file_ext in cls.get_allowed_extensions()
    
    @classmethod
    def determine_storage_type(cls, file_size):
        """Determine storage type based on file size"""
        return 'database' if file_size <= cls.STORAGE_THRESHOLD else 'filesystem'
    
    @classmethod
    def generate_file_path(cls, row_id, filename):
        """Generate filesystem path for large attachments using row_id_filename structure"""
        timestamp = datetime.now()
        safe_filename = secure_filename(filename)
        return f"large_attachments/{timestamp.year}/{timestamp.month:02d}/{row_id}_{safe_filename}"
    
    def save_file(self, file_data, filename):
        """Save file data to appropriate storage"""
        self.filename = filename
        self.file_size = len(file_data)
        self.storage_type = self.determine_storage_type(self.file_size)
        
        if self.storage_type == 'database':
            self.file_data = file_data
            self.file_path = None
        else:
            # Save to filesystem
            self.file_path = self.generate_file_path(self.id, filename)
            self.file_data = None
            
            # Ensure directory exists
            file_dir = Path(self.file_path).parent
            file_dir.mkdir(parents=True, exist_ok=True)
            
            # Write file
            with open(self.file_path, 'wb') as f:
                f.write(file_data)
    
    def get_file_data(self):
        """Get file data from appropriate storage"""
        if self.storage_type == 'database':
            return self.file_data
        else:
            # Read from filesystem
            if self.file_path and os.path.exists(self.file_path):
                with open(self.file_path, 'rb') as f:
                    return f.read()
            return None
    
    def delete_file(self):
        """Delete file from storage"""
        if self.storage_type == 'filesystem' and self.file_path:
            try:
                if os.path.exists(self.file_path):
                    os.remove(self.file_path)
                    
                    # Try to remove empty directories
                    file_dir = Path(self.file_path).parent
                    if file_dir.exists() and not any(file_dir.iterdir()):
                        file_dir.rmdir()
                        
                        # Try to remove parent month directory if empty
                        month_dir = file_dir.parent
                        if month_dir.exists() and not any(month_dir.iterdir()):
                            month_dir.rmdir()
                            
                            # Try to remove parent year directory if empty
                            year_dir = month_dir.parent
                            if year_dir.exists() and not any(year_dir.iterdir()):
                                year_dir.rmdir()
            except OSError:
                pass  # File might already be deleted
    
    def get_file_url(self):
        """Get URL for file download"""
        return f"/attachments/{self.id}/download"
    
    def get_file_extension(self):
        """Get file extension"""
        return Path(self.filename).suffix.lower()
    
    def is_image(self):
        """Check if file is an image"""
        return self.get_file_extension() in self.ALLOWED_EXTENSIONS['images']
    
    def is_document(self):
        """Check if file is a document"""
        return self.get_file_extension() in self.ALLOWED_EXTENSIONS['documents']
    
    def get_file_size_display(self):
        """Get human-readable file size"""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if self.file_size < 1024.0:
                return f"{self.file_size:.1f} {unit}"
            self.file_size /= 1024.0
        return f"{self.file_size:.1f} TB"
    
    def __repr__(self):
        return f'<Attachment {self.filename} ({self.get_file_size_display()})>' 