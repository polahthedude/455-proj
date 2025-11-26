"""Authentication and user management"""
import re
import bcrypt
import jwt
from datetime import datetime, timedelta
from functools import wraps
from flask import request, jsonify, current_app
from server.models import db, User
from shared.constants import PASSWORD_MIN_LENGTH, STATUS_ERROR, STATUS_SUCCESS


def hash_password(password: str, salt: bytes = None) -> tuple:
    """Hash password with bcrypt"""
    if salt is None:
        salt = bcrypt.gensalt(rounds=10)
    password_hash = bcrypt.hashpw(password.encode('utf-8'), salt)
    return password_hash.decode('utf-8'), salt.decode('utf-8')


def verify_password(password: str, password_hash: str) -> bool:
    """Verify password against hash"""
    return bcrypt.checkpw(password.encode('utf-8'), password_hash.encode('utf-8'))


def validate_password(password: str) -> tuple:
    """Validate password strength"""
    if len(password) < PASSWORD_MIN_LENGTH:
        return False, f"Password must be at least {PASSWORD_MIN_LENGTH} characters"
    
    if not re.search(r'[A-Z]', password):
        return False, "Password must contain uppercase letters"
    
    if not re.search(r'[a-z]', password):
        return False, "Password must contain lowercase letters"
    
    if not re.search(r'\d', password):
        return False, "Password must contain numbers"
    
    if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
        return False, "Password must contain special characters"
    
    return True, "Password is valid"


def generate_token(user_id: int, username: str) -> str:
    """Generate JWT token"""
    expiration = datetime.utcnow() + timedelta(hours=current_app.config['JWT_EXPIRATION_HOURS'])
    
    payload = {
        'user_id': user_id,
        'username': username,
        'exp': expiration,
        'iat': datetime.utcnow()
    }
    
    token = jwt.encode(payload, current_app.config['JWT_SECRET_KEY'], algorithm='HS256')
    return token


def decode_token(token: str) -> dict:
    """Decode and verify JWT token"""
    try:
        payload = jwt.decode(token, current_app.config['JWT_SECRET_KEY'], algorithms=['HS256'])
        return payload
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None


def token_required(f):
    """Decorator to require valid JWT token"""
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        
        # Get token from header
        if 'Authorization' in request.headers:
            auth_header = request.headers['Authorization']
            try:
                token = auth_header.split(' ')[1]  # Bearer <token>
            except IndexError:
                return jsonify({'status': STATUS_ERROR, 'message': 'Invalid token format'}), 401
        
        if not token:
            return jsonify({'status': STATUS_ERROR, 'message': 'Token is missing'}), 401
        
        # Decode token
        payload = decode_token(token)
        if not payload:
            return jsonify({'status': STATUS_ERROR, 'message': 'Token is invalid or expired'}), 401
        
        # Get user
        current_user = User.query.get(payload['user_id'])
        if not current_user:
            return jsonify({'status': STATUS_ERROR, 'message': 'User not found'}), 401
        
        return f(current_user=current_user, *args, **kwargs)
    
    return decorated


def register_user(username: str, email: str, password: str, public_key: str = None) -> tuple:
    """Register new user"""
    # Validate username
    if not username or len(username) < 3:
        return None, "Username must be at least 3 characters"
    
    if not re.match(r'^[a-zA-Z0-9_]+$', username):
        return None, "Username can only contain letters, numbers, and underscores"
    
    # Validate email
    if not email or not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', email):
        return None, "Invalid email address"
    
    # Validate password
    is_valid, message = validate_password(password)
    if not is_valid:
        return None, message
    
    # Check if user exists
    if User.query.filter_by(username=username).first():
        return None, "Username already exists"
    
    if User.query.filter_by(email=email).first():
        return None, "Email already exists"
    
    # Hash password
    print(f"[AUTH] Hashing password for user: {username}...")
    password_hash, salt = hash_password(password)
    print(f"[AUTH] Password hashed successfully")
    
    # Create user
    user = User(
        username=username,
        email=email,
        password_hash=password_hash,
        salt=salt,
        public_key=public_key
    )
    
    try:
        db.session.add(user)
        db.session.commit()
        return user, "User registered successfully"
    except Exception as e:
        db.session.rollback()
        return None, f"Error registering user: {str(e)}"


def login_user(username: str, password: str) -> tuple:
    """Login user and generate token"""
    user = User.query.filter_by(username=username).first()
    
    if not user:
        return None, "Invalid username or password"
    
    if not verify_password(password, user.password_hash):
        return None, "Invalid username or password"
    
    # Update last login
    user.last_login = datetime.utcnow()
    db.session.commit()
    
    # Generate token
    token = generate_token(user.id, user.username)
    
    return {'user': user.to_dict(), 'token': token}, "Login successful"
