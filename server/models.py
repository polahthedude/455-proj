"""Database models"""
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class User(db.Model):
    """User model"""
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    salt = db.Column(db.String(255), nullable=False)
    public_key = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_login = db.Column(db.DateTime, nullable=True)
    storage_used = db.Column(db.Integer, default=0)  # bytes
    
    # Relationships
    files = db.relationship('File', back_populates='user', cascade='all, delete-orphan')
    folders = db.relationship('Folder', back_populates='user', cascade='all, delete-orphan')
    shared_files = db.relationship('Share', foreign_keys='Share.shared_by_user_id', 
                                   back_populates='shared_by')
    received_shares = db.relationship('Share', foreign_keys='Share.shared_with_user_id',
                                     back_populates='shared_with')
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'created_at': self.created_at.isoformat(),
            'storage_used': self.storage_used
        }


class File(db.Model):
    """File metadata model"""
    __tablename__ = 'files'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    filename_encrypted = db.Column(db.String(500), nullable=False)
    file_uuid = db.Column(db.String(36), unique=True, nullable=False, index=True)
    file_hash = db.Column(db.String(64), nullable=False)  # SHA-256
    size = db.Column(db.Integer, nullable=False)
    folder_path = db.Column(db.String(1000), default='/', nullable=False, index=True)  # Folder location
    encryption_metadata = db.Column(db.JSON, nullable=False)  # IV, auth_tag, etc.
    uploaded_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    version = db.Column(db.Integer, default=1)
    is_current = db.Column(db.Boolean, default=True)
    parent_file_id = db.Column(db.Integer, db.ForeignKey('files.id'), nullable=True)
    
    # Relationships
    user = db.relationship('User', back_populates='files')
    shares = db.relationship('Share', back_populates='file', cascade='all, delete-orphan')
    versions = db.relationship('File', remote_side=[id], backref='parent')
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            'id': self.id,
            'file_uuid': self.file_uuid,
            'filename_encrypted': self.filename_encrypted,
            'file_hash': self.file_hash,
            'size': self.size,
            'folder_path': self.folder_path,
            'encryption_metadata': self.encryption_metadata,
            'uploaded_at': self.uploaded_at.isoformat(),
            'version': self.version,
            'is_current': self.is_current
        }


class Folder(db.Model):
    """Folder model"""
    __tablename__ = 'folders'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    folder_uuid = db.Column(db.String(36), unique=True, nullable=False, index=True)
    name_encrypted = db.Column(db.String(500), nullable=False)  # Encrypted folder name
    path = db.Column(db.String(1000), nullable=False, index=True)  # Full path (e.g., /Documents/Photos/)
    parent_path = db.Column(db.String(1000), nullable=False, index=True)  # Parent folder path
    encryption_metadata = db.Column(db.JSON, nullable=False)  # IV, tag for name encryption
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    modified_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = db.relationship('User', back_populates='folders')
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            'id': self.id,
            'folder_uuid': self.folder_uuid,
            'name_encrypted': self.name_encrypted,
            'path': self.path,
            'parent_path': self.parent_path,
            'encryption_metadata': self.encryption_metadata,
            'created_at': self.created_at.isoformat(),
            'modified_at': self.modified_at.isoformat()
        }


class Share(db.Model):
    """File sharing permissions"""
    __tablename__ = 'shares'
    
    id = db.Column(db.Integer, primary_key=True)
    file_id = db.Column(db.Integer, db.ForeignKey('files.id'), nullable=False)
    shared_by_user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    shared_with_user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    access_level = db.Column(db.String(20), default='read')  # read, write
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    expires_at = db.Column(db.DateTime, nullable=True)
    
    # Relationships
    file = db.relationship('File', back_populates='shares')
    shared_by = db.relationship('User', foreign_keys=[shared_by_user_id], back_populates='shared_files')
    shared_with = db.relationship('User', foreign_keys=[shared_with_user_id], back_populates='received_shares')
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            'id': self.id,
            'file_id': self.file_id,
            'shared_by_user_id': self.shared_by_user_id,
            'shared_with_user_id': self.shared_with_user_id,
            'access_level': self.access_level,
            'created_at': self.created_at.isoformat(),
            'expires_at': self.expires_at.isoformat() if self.expires_at else None
        }
