"""Shared constants and configurations"""

# API Endpoints
API_BASE = "/api"
AUTH_REGISTER = f"{API_BASE}/auth/register"
AUTH_LOGIN = f"{API_BASE}/auth/login"
AUTH_LOGOUT = f"{API_BASE}/auth/logout"
AUTH_VERIFY = f"{API_BASE}/auth/verify"
FILES_UPLOAD = f"{API_BASE}/files/upload"
FILES_LIST = f"{API_BASE}/files/list"
FILES_DOWNLOAD = f"{API_BASE}/files"
FILES_DELETE = f"{API_BASE}/files"
FILES_VERSIONS = f"{API_BASE}/files"

# Encryption Constants
AES_KEY_SIZE = 32  # 256 bits
AES_BLOCK_SIZE = 16
RSA_KEY_SIZE = 2048
CHUNK_SIZE = 8 * 1024 * 1024  # 8MB chunks
PBKDF2_ITERATIONS = 10000  # Reduced from 100000 for better performance

# File Storage
MAX_FILE_SIZE = 100 * 1024 * 1024  # 100MB
USER_QUOTA = 1024 * 1024 * 1024  # 1GB
MAX_VERSIONS = 5

# Security
PASSWORD_MIN_LENGTH = 12
JWT_EXPIRATION_HOURS = 24
BCRYPT_ROUNDS = 12
RATE_LIMIT_PER_MINUTE = 100

# Status Codes
STATUS_SUCCESS = "success"
STATUS_ERROR = "error"
STATUS_UNAUTHORIZED = "unauthorized"
