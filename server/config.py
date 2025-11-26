"""Server configuration management"""
import os
import yaml
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

class Config:
    """Server configuration"""
    
    # Load from config.yaml
    config_path = Path(__file__).parent.parent / 'config.yaml'
    with open(config_path, 'r') as f:
        _config = yaml.safe_load(f)
    
    # Flask settings
    SECRET_KEY = os.getenv('FLASK_SECRET_KEY', _config['server']['secret_key'])
    HOST = _config['server']['host']
    PORT = _config['server']['port']
    DEBUG = _config['server']['debug']
    MAX_CONTENT_LENGTH = _config['server']['max_content_length']
    
    # Database
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URI', _config['database']['uri'])
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Security
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY', SECRET_KEY)
    JWT_EXPIRATION_HOURS = _config['security']['jwt_expiration_hours']
    BCRYPT_ROUNDS = _config['security']['bcrypt_rounds']
    RATE_LIMIT = _config['security']['rate_limit_per_minute']
    PASSWORD_MIN_LENGTH = _config['security']['password_min_length']
    
    # Storage
    UPLOAD_FOLDER = Path(__file__).parent.parent / _config['server']['upload_folder']
    MAX_FILE_SIZE = _config['storage']['max_file_size']
    USER_QUOTA = _config['storage']['user_quota']
    MAX_VERSIONS = _config['storage']['max_versions']
    
    @classmethod
    def init_app(cls):
        """Initialize application directories"""
        cls.UPLOAD_FOLDER.mkdir(parents=True, exist_ok=True)
