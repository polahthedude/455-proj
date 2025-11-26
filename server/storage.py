"""File storage management"""
import os
import uuid
import hashlib
from pathlib import Path
from datetime import datetime
from werkzeug.utils import secure_filename
from server.models import db, File, User
from server.config import Config


class StorageManager:
    """Manages encrypted file storage"""
    
    def __init__(self, upload_folder: Path):
        self.upload_folder = upload_folder
        self.upload_folder.mkdir(parents=True, exist_ok=True)
    
    def get_user_folder(self, user_id: int) -> Path:
        """Get user's storage folder"""
        user_folder = self.upload_folder / f"user_{user_id}"
        user_folder.mkdir(parents=True, exist_ok=True)
        return user_folder
    
    def get_versions_folder(self, user_id: int) -> Path:
        """Get user's versions folder"""
        versions_folder = self.get_user_folder(user_id) / "versions"
        versions_folder.mkdir(parents=True, exist_ok=True)
        return versions_folder
    
    def save_file(self, user_id: int, file_data: bytes, file_uuid: str = None) -> tuple:
        """Save encrypted file to disk"""
        if file_uuid is None:
            file_uuid = str(uuid.uuid4())
        
        user_folder = self.get_user_folder(user_id)
        file_path = user_folder / f"{file_uuid}.enc"
        
        try:
            # Write file atomically
            temp_path = file_path.with_suffix('.tmp')
            with open(temp_path, 'wb') as f:
                f.write(file_data)
            
            # Rename to final name
            temp_path.replace(file_path)
            
            return file_uuid, str(file_path)
        except Exception as e:
            if temp_path.exists():
                temp_path.unlink()
            raise Exception(f"Error saving file: {str(e)}")
    
    def get_file(self, user_id: int, file_uuid: str) -> bytes:
        """Read encrypted file from disk"""
        user_folder = self.get_user_folder(user_id)
        file_path = user_folder / f"{file_uuid}.enc"
        
        if not file_path.exists():
            # Check versions folder
            versions_folder = self.get_versions_folder(user_id)
            version_files = list(versions_folder.glob(f"{file_uuid}_v*.enc"))
            if version_files:
                file_path = version_files[0]
            else:
                raise FileNotFoundError(f"File not found: {file_uuid}")
        
        with open(file_path, 'rb') as f:
            return f.read()
    
    def delete_file(self, user_id: int, file_uuid: str) -> bool:
        """Delete file from disk"""
        user_folder = self.get_user_folder(user_id)
        file_path = user_folder / f"{file_uuid}.enc"
        
        if file_path.exists():
            file_path.unlink()
            return True
        return False
    
    def save_version(self, user_id: int, file_uuid: str, version: int, file_data: bytes) -> str:
        """Save file version"""
        versions_folder = self.get_versions_folder(user_id)
        version_path = versions_folder / f"{file_uuid}_v{version}.enc"
        
        with open(version_path, 'wb') as f:
            f.write(file_data)
        
        return str(version_path)
    
    def cleanup_old_versions(self, user_id: int, file_uuid: str, max_versions: int):
        """Remove old versions beyond max_versions"""
        versions_folder = self.get_versions_folder(user_id)
        version_files = sorted(
            versions_folder.glob(f"{file_uuid}_v*.enc"),
            key=lambda p: p.stat().st_mtime
        )
        
        # Keep only the most recent versions
        if len(version_files) > max_versions:
            for old_file in version_files[:-max_versions]:
                old_file.unlink()
    
    def get_user_storage(self, user_id: int) -> int:
        """Calculate total storage used by user"""
        user_folder = self.get_user_folder(user_id)
        total_size = 0
        
        for file_path in user_folder.rglob("*.enc"):
            total_size += file_path.stat().st_size
        
        return total_size
    
    def check_quota(self, user: User, file_size: int) -> bool:
        """Check if user has enough quota"""
        return (user.storage_used + file_size) <= Config.USER_QUOTA


def calculate_file_hash(file_data: bytes) -> str:
    """Calculate SHA-256 hash of file"""
    return hashlib.sha256(file_data).hexdigest()
