"""Flask application and API endpoints"""
import os
import uuid
from datetime import datetime
from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
from io import BytesIO
from server.config import Config
from server.models import db, User, File, Folder, Share
from server.auth import (
    register_user, login_user, token_required,
    decode_token
)
from server.storage import StorageManager, calculate_file_hash
from shared.constants import (
    STATUS_SUCCESS, STATUS_ERROR,
    API_BASE, AUTH_REGISTER, AUTH_LOGIN, AUTH_VERIFY,
    FILES_UPLOAD, FILES_LIST
)

app = Flask(__name__)
app.config.from_object(Config)

# Initialize extensions
CORS(app)
db.init_app(app)

# Initialize storage manager
storage = StorageManager(Config.UPLOAD_FOLDER)


@app.before_request
def before_request():
    """Request preprocessing"""
    pass


# ==================== Authentication Endpoints ====================

@app.route(AUTH_REGISTER, methods=['POST'])
def api_register():
    """Register new user"""
    data = request.get_json()
    
    if not data:
        return jsonify({'status': STATUS_ERROR, 'message': 'No data provided'}), 400
    
    print(f"[REGISTER] Registration request received for user: {data.get('username', 'unknown')}")
    
    username = data.get('username')
    email = data.get('email')
    password = data.get('password')
    public_key = data.get('public_key')
    
    if not all([username, email, password]):
        return jsonify({'status': STATUS_ERROR, 'message': 'Missing required fields'}), 400
    
    user, message = register_user(username, email, password, public_key)
    
    if not user:
        return jsonify({'status': STATUS_ERROR, 'message': message}), 400
    
    return jsonify({
        'status': STATUS_SUCCESS,
        'message': message,
        'user': user.to_dict()
    }), 201


@app.route(AUTH_LOGIN, methods=['POST'])
def api_login():
    """Login user"""
    data = request.get_json()
    
    if not data:
        return jsonify({'status': STATUS_ERROR, 'message': 'No data provided'}), 400
    
    username = data.get('username')
    password = data.get('password')
    
    if not all([username, password]):
        return jsonify({'status': STATUS_ERROR, 'message': 'Missing username or password'}), 400
    
    result, message = login_user(username, password)
    
    if not result:
        return jsonify({'status': STATUS_ERROR, 'message': message}), 401
    
    return jsonify({
        'status': STATUS_SUCCESS,
        'message': message,
        'token': result['token'],
        'user': result['user']
    }), 200


@app.route(AUTH_VERIFY, methods=['GET'])
@token_required
def api_verify(current_user):
    """Verify token validity"""
    return jsonify({
        'status': STATUS_SUCCESS,
        'user': current_user.to_dict()
    }), 200


# ==================== File Management Endpoints ====================

@app.route(FILES_UPLOAD, methods=['POST'])
@token_required
def api_upload_file(current_user):
    """Upload encrypted file"""
    # Check if file is present
    if 'file' not in request.files:
        return jsonify({'status': STATUS_ERROR, 'message': 'No file provided'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'status': STATUS_ERROR, 'message': 'No file selected'}), 400
    
    # Get metadata
    metadata = request.form.get('metadata')
    if not metadata:
        return jsonify({'status': STATUS_ERROR, 'message': 'No metadata provided'}), 400
    
    import json
    try:
        metadata = json.loads(metadata)
    except json.JSONDecodeError:
        return jsonify({'status': STATUS_ERROR, 'message': 'Invalid metadata format'}), 400
    
    # Read file data
    file_data = file.read()
    file_size = len(file_data)
    
    # Check quota
    if not storage.check_quota(current_user, file_size):
        return jsonify({'status': STATUS_ERROR, 'message': 'Storage quota exceeded'}), 413
    
    # Calculate hash
    file_hash = calculate_file_hash(file_data)
    
    # Verify hash matches metadata
    if file_hash != metadata.get('file_hash'):
        return jsonify({'status': STATUS_ERROR, 'message': 'File hash mismatch'}), 400
    
    # Generate UUID
    file_uuid = str(uuid.uuid4())
    
    # Save file
    try:
        file_uuid, file_path = storage.save_file(current_user.id, file_data, file_uuid)
    except Exception as e:
        return jsonify({'status': STATUS_ERROR, 'message': str(e)}), 500
    
    # Create database entry
    db_file = File(
        user_id=current_user.id,
        filename_encrypted=metadata.get('encrypted_filename'),
        file_uuid=file_uuid,
        file_hash=file_hash,
        size=file_size,
        folder_path=metadata.get('folder_path', '/'),
        encryption_metadata={
            'encrypted_key': metadata.get('encrypted_key'),
            'iv': metadata.get('iv'),
            'auth_tag': metadata.get('auth_tag'),
            'encrypted_filename': metadata.get('encrypted_filename'),
            'filename_iv': metadata.get('filename_iv'),
            'filename_tag': metadata.get('filename_tag')
        }
    )
    
    try:
        db.session.add(db_file)
        current_user.storage_used += file_size
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        storage.delete_file(current_user.id, file_uuid)
        return jsonify({'status': STATUS_ERROR, 'message': f'Database error: {str(e)}'}), 500
    
    return jsonify({
        'status': STATUS_SUCCESS,
        'message': 'File uploaded successfully',
        'file': db_file.to_dict()
    }), 201


@app.route(FILES_LIST, methods=['GET'])
@token_required
def api_list_files(current_user):
    """List user's files"""
    # Get only current versions
    files = File.query.filter_by(
        user_id=current_user.id,
        is_current=True
    ).order_by(File.uploaded_at.desc()).all()
    
    return jsonify({
        'status': STATUS_SUCCESS,
        'files': [f.to_dict() for f in files],
        'total_files': len(files),
        'storage_used': current_user.storage_used
    }), 200


@app.route(f'{FILES_LIST}/<file_uuid>', methods=['GET'])
@token_required
def api_download_file(current_user, file_uuid):
    """Download encrypted file"""
    # Get file metadata
    db_file = File.query.filter_by(
        file_uuid=file_uuid,
        user_id=current_user.id
    ).first()
    
    if not db_file:
        # Check if file is shared with user
        share = Share.query.join(File).filter(
            File.file_uuid == file_uuid,
            Share.shared_with_user_id == current_user.id
        ).first()
        
        if not share:
            return jsonify({'status': STATUS_ERROR, 'message': 'File not found'}), 404
        
        db_file = share.file
    
    # Get file data
    try:
        file_data = storage.get_file(db_file.user_id, file_uuid)
    except FileNotFoundError:
        return jsonify({'status': STATUS_ERROR, 'message': 'File not found on disk'}), 404
    except Exception as e:
        return jsonify({'status': STATUS_ERROR, 'message': str(e)}), 500
    
    # Return file
    return send_file(
        BytesIO(file_data),
        mimetype='application/octet-stream',
        as_attachment=True,
        download_name=f"{file_uuid}.enc"
    )


@app.route(f'{FILES_LIST}/<file_uuid>', methods=['DELETE'])
@token_required
def api_delete_file(current_user, file_uuid):
    """Delete file"""
    # Get file
    db_file = File.query.filter_by(
        file_uuid=file_uuid,
        user_id=current_user.id
    ).first()
    
    if not db_file:
        return jsonify({'status': STATUS_ERROR, 'message': 'File not found'}), 404
    
    # Delete from disk
    storage.delete_file(current_user.id, file_uuid)
    
    # Update storage used
    current_user.storage_used -= db_file.size
    
    # Delete from database
    db.session.delete(db_file)
    db.session.commit()
    
    return jsonify({
        'status': STATUS_SUCCESS,
        'message': 'File deleted successfully'
    }), 200


@app.route(f'{FILES_LIST}/<file_uuid>/metadata', methods=['GET'])
@token_required
def api_get_metadata(current_user, file_uuid):
    """Get file metadata"""
    db_file = File.query.filter_by(
        file_uuid=file_uuid,
        user_id=current_user.id
    ).first()
    
    if not db_file:
        return jsonify({'status': STATUS_ERROR, 'message': 'File not found'}), 404
    
    return jsonify({
        'status': STATUS_SUCCESS,
        'file': db_file.to_dict()
    }), 200


# ==================== Folder Management Endpoints ====================

@app.route(f'{API_BASE}/folders', methods=['POST'])
@token_required
def api_create_folder(current_user):
    """Create a new folder"""
    data = request.get_json()
    
    if not data:
        return jsonify({'status': STATUS_ERROR, 'message': 'No data provided'}), 400
    
    name_encrypted = data.get('name_encrypted')
    path = data.get('path')
    parent_path = data.get('parent_path')
    encryption_metadata = data.get('encryption_metadata')
    
    if not all([name_encrypted, path, parent_path, encryption_metadata]):
        return jsonify({'status': STATUS_ERROR, 'message': 'Missing required fields'}), 400
    
    # Check if folder already exists
    existing = Folder.query.filter_by(
        user_id=current_user.id,
        path=path
    ).first()
    
    if existing:
        return jsonify({'status': STATUS_ERROR, 'message': 'Folder already exists'}), 400
    
    # Create folder
    folder_uuid = str(uuid.uuid4())
    folder = Folder(
        user_id=current_user.id,
        folder_uuid=folder_uuid,
        name_encrypted=name_encrypted,
        path=path,
        parent_path=parent_path,
        encryption_metadata=encryption_metadata
    )
    
    try:
        db.session.add(folder)
        db.session.commit()
        return jsonify({
            'status': STATUS_SUCCESS,
            'message': 'Folder created successfully',
            'folder': folder.to_dict()
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'status': STATUS_ERROR, 'message': f'Database error: {str(e)}'}), 500


@app.route(f'{API_BASE}/folders', methods=['GET'])
@token_required
def api_list_folders(current_user):
    """List user's folders"""
    folders = Folder.query.filter_by(
        user_id=current_user.id
    ).order_by(Folder.path).all()
    
    return jsonify({
        'status': STATUS_SUCCESS,
        'folders': [f.to_dict() for f in folders],
        'total_folders': len(folders)
    }), 200


@app.route(f'{API_BASE}/folders/<folder_uuid>', methods=['PUT'])
@token_required
def api_rename_folder(current_user, folder_uuid):
    """Rename a folder"""
    folder = Folder.query.filter_by(
        folder_uuid=folder_uuid,
        user_id=current_user.id
    ).first()
    
    if not folder:
        return jsonify({'status': STATUS_ERROR, 'message': 'Folder not found'}), 404
    
    data = request.get_json()
    name_encrypted = data.get('name_encrypted')
    new_path = data.get('path')
    encryption_metadata = data.get('encryption_metadata')
    
    if not all([name_encrypted, new_path, encryption_metadata]):
        return jsonify({'status': STATUS_ERROR, 'message': 'Missing required fields'}), 400
    
    old_path = folder.path
    
    # Update folder
    folder.name_encrypted = name_encrypted
    folder.path = new_path
    folder.encryption_metadata = encryption_metadata
    folder.modified_at = datetime.utcnow()
    
    # Update all subfolders' paths
    subfolders = Folder.query.filter(
        Folder.user_id == current_user.id,
        Folder.path.startswith(old_path),
        Folder.id != folder.id
    ).all()
    
    for subfolder in subfolders:
        subfolder.path = subfolder.path.replace(old_path, new_path, 1)
        if subfolder.parent_path == old_path:
            subfolder.parent_path = new_path
    
    try:
        db.session.commit()
        return jsonify({
            'status': STATUS_SUCCESS,
            'message': 'Folder renamed successfully',
            'folder': folder.to_dict()
        }), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'status': STATUS_ERROR, 'message': f'Database error: {str(e)}'}), 500


@app.route(f'{API_BASE}/folders/<folder_uuid>', methods=['DELETE'])
@token_required
def api_delete_folder(current_user, folder_uuid):
    """Delete a folder and all its contents"""
    folder = Folder.query.filter_by(
        folder_uuid=folder_uuid,
        user_id=current_user.id
    ).first()
    
    if not folder:
        return jsonify({'status': STATUS_ERROR, 'message': 'Folder not found'}), 404
    
    # Delete all subfolders
    subfolders = Folder.query.filter(
        Folder.user_id == current_user.id,
        Folder.path.startswith(folder.path)
    ).all()
    
    for subfolder in subfolders:
        db.session.delete(subfolder)
    
    try:
        db.session.commit()
        return jsonify({
            'status': STATUS_SUCCESS,
            'message': 'Folder deleted successfully'
        }), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'status': STATUS_ERROR, 'message': f'Database error: {str(e)}'}), 500


# ==================== Health Check ====================

@app.route(f'{API_BASE}/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': STATUS_SUCCESS,
        'message': 'Server is running'
    }), 200


# ==================== Database Initialization ====================

def init_db():
    """Initialize database"""
    with app.app_context():
        db.create_all()
        print("Database initialized successfully")


# ==================== Main ====================

if __name__ == '__main__':
    Config.init_app()
    
    # Initialize database
    with app.app_context():
        db.create_all()
    
    print(f"Starting server on {Config.HOST}:{Config.PORT}")
    app.run(host=Config.HOST, port=Config.PORT, debug=Config.DEBUG)
