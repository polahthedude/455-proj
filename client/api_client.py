"""API client for server communication"""
import requests
import json
from pathlib import Path
from typing import Optional, Dict, List, Tuple
from shared.constants import (
    API_BASE, AUTH_REGISTER, AUTH_LOGIN, AUTH_VERIFY,
    FILES_UPLOAD, FILES_LIST, STATUS_SUCCESS
)


class APIClient:
    """Handles all API communication with server"""
    
    def __init__(self, base_url: str):
        self.base_url = base_url.rstrip('/')
        self.session = requests.Session()
        self.timeout = 60
    
    def _make_request(self, method: str, endpoint: str, **kwargs) -> Tuple[bool, dict]:
        """Make HTTP request to server"""
        url = f"{self.base_url}{endpoint}"
        
        try:
            if 'timeout' not in kwargs:
                kwargs['timeout'] = self.timeout
            
            response = self.session.request(method, url, **kwargs)
            
            # Try to parse JSON response
            try:
                data = response.json()
            except json.JSONDecodeError:
                data = {'message': response.text if response.text else 'Unknown error'}
            
            # Add status code to response for better error handling
            data['status_code'] = response.status_code
            
            # Handle specific status codes with clear messages
            if response.status_code == 401:
                if 'message' not in data:
                    data['message'] = 'Authentication failed. Please check your credentials or login again.'
                data['auth_error'] = True
            elif response.status_code == 403:
                if 'message' not in data:
                    data['message'] = 'Access denied. You do not have permission for this action.'
            elif response.status_code == 404:
                if 'message' not in data:
                    data['message'] = 'Resource not found.'
            elif response.status_code == 413:
                if 'message' not in data:
                    data['message'] = 'File too large. Maximum file size is 100MB.'
            elif response.status_code >= 500:
                if 'message' not in data:
                    data['message'] = 'Server error. Please try again later.'
            
            success = response.status_code < 400
            return success, data
            
        except requests.exceptions.ConnectionError:
            return False, {
                'message': 'Could not connect to server. Please check if the server is running and try again.',
                'connection_error': True
            }
        except requests.exceptions.Timeout:
            return False, {
                'message': 'Request timed out. The server took too long to respond.',
                'timeout_error': True
            }
        except Exception as e:
            return False, {
                'message': f'Unexpected error: {str(e)}',
                'exception': str(type(e).__name__)
            }
    
    # ==================== Authentication ====================
    
    def register(self, username: str, email: str, password: str, public_key: str = None) -> Tuple[bool, dict]:
        """Register new user"""
        data = {
            'username': username,
            'email': email,
            'password': password,
            'public_key': public_key
        }
        
        return self._make_request('POST', AUTH_REGISTER, json=data)
    
    def login(self, username: str, password: str) -> Tuple[bool, dict]:
        """Login user"""
        data = {
            'username': username,
            'password': password
        }
        
        return self._make_request('POST', AUTH_LOGIN, json=data)
    
    def verify_token(self, token: str) -> Tuple[bool, dict]:
        """Verify JWT token"""
        headers = {'Authorization': f'Bearer {token}'}
        return self._make_request('GET', AUTH_VERIFY, headers=headers)
    
    # ==================== File Operations ====================
    
    def upload_file(self, file_path: str, encrypted_data: bytes, metadata: dict, token: str,
                   progress_callback=None) -> Tuple[bool, dict]:
        """Upload encrypted file"""
        headers = {'Authorization': f'Bearer {token}'}
        
        # Prepare multipart form data
        files = {
            'file': ('encrypted_file.enc', encrypted_data, 'application/octet-stream')
        }
        
        data = {
            'metadata': json.dumps(metadata)
        }
        
        return self._make_request('POST', FILES_UPLOAD, headers=headers, files=files, data=data)
    
    def list_files(self, token: str) -> Tuple[bool, dict]:
        """List user's files"""
        headers = {'Authorization': f'Bearer {token}'}
        return self._make_request('GET', FILES_LIST, headers=headers)
    
    def download_file(self, file_uuid: str, token: str) -> Tuple[bool, bytes]:
        """Download encrypted file"""
        headers = {'Authorization': f'Bearer {token}'}
        endpoint = f"{FILES_LIST}/{file_uuid}"
        
        url = f"{self.base_url}{endpoint}"
        
        try:
            response = self.session.get(url, headers=headers, timeout=self.timeout)
            
            if response.status_code == 200:
                return True, response.content
            else:
                return False, response.content
                
        except Exception as e:
            return False, str(e).encode()
    
    def delete_file(self, file_uuid: str, token: str) -> Tuple[bool, dict]:
        """Delete file"""
        headers = {'Authorization': f'Bearer {token}'}
        endpoint = f"{FILES_LIST}/{file_uuid}"
        return self._make_request('DELETE', endpoint, headers=headers)
    
    def get_metadata(self, file_uuid: str, token: str) -> Tuple[bool, dict]:
        """Get file metadata"""
        headers = {'Authorization': f'Bearer {token}'}
        endpoint = f"{FILES_LIST}/{file_uuid}/metadata"
        return self._make_request('GET', endpoint, headers=headers)
    
    # ==================== Folder Operations ====================
    
    def create_folder(self, name_encrypted: str, path: str, parent_path: str, 
                     encryption_metadata: dict, token: str) -> Tuple[bool, dict]:
        """Create a new folder"""
        headers = {'Authorization': f'Bearer {token}'}
        data = {
            'name_encrypted': name_encrypted,
            'path': path,
            'parent_path': parent_path,
            'encryption_metadata': encryption_metadata
        }
        return self._make_request('POST', f'{API_BASE}/folders', headers=headers, json=data)
    
    def list_folders(self, token: str) -> Tuple[bool, dict]:
        """List user's folders"""
        headers = {'Authorization': f'Bearer {token}'}
        return self._make_request('GET', f'{API_BASE}/folders', headers=headers)
    
    def rename_folder(self, folder_uuid: str, name_encrypted: str, path: str,
                     encryption_metadata: dict, token: str) -> Tuple[bool, dict]:
        """Rename a folder"""
        headers = {'Authorization': f'Bearer {token}'}
        data = {
            'name_encrypted': name_encrypted,
            'path': path,
            'encryption_metadata': encryption_metadata
        }
        return self._make_request('PUT', f'{API_BASE}/folders/{folder_uuid}', 
                                 headers=headers, json=data)
    
    def delete_folder(self, folder_uuid: str, token: str) -> Tuple[bool, dict]:
        """Delete a folder"""
        headers = {'Authorization': f'Bearer {token}'}
        return self._make_request('DELETE', f'{API_BASE}/folders/{folder_uuid}', headers=headers)
    
    # ==================== Health Check ====================
    
    def health_check(self) -> bool:
        """Check if server is reachable"""
        success, _ = self._make_request('GET', '/api/health')
        return success
