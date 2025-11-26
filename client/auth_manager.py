"""Client-side authentication manager"""
import os
from pathlib import Path
from typing import Optional
from client.crypto_handler import CryptoHandler, KeyManager


class AuthManager:
    """Manages user authentication state"""
    
    def __init__(self):
        self.username = None
        self.token = None
        self.user_id = None
        self.crypto_handler = CryptoHandler()
        self.key_manager = KeyManager()
        self.is_authenticated = False
    
    def login(self, username: str, password: str, token: str, user_id: int) -> bool:
        """Login user and load keys"""
        self.username = username
        self.token = token
        self.user_id = user_id
        
        # Try to load keys
        try:
            if self.key_manager.keys_exist():
                print(f"[AUTH] Keys exist, attempting to load...")
                try:
                    private_key, public_key = self.key_manager.load_keys(password)
                    self.crypto_handler.load_private_key(private_key)
                    self.is_authenticated = True
                    print(f"[AUTH] Keys loaded successfully")
                    return True
                except Exception as decrypt_error:
                    print(f"[AUTH] Failed to decrypt keys: {decrypt_error}")
                    print(f"[AUTH] This could mean wrong password or corrupted keys")
                    # If decryption fails, it's likely wrong password
                    raise ValueError("Incorrect password or corrupted keys")
            else:
                # Generate new keys on first login
                print(f"[AUTH] No keys found, generating new keys...")
                private_key, public_key = self.crypto_handler.generate_rsa_keypair()
                self.key_manager.save_keys(private_key, public_key, password)
                self.is_authenticated = True
                print(f"[AUTH] New keys generated and saved")
                return True
        except Exception as e:
            print(f"[AUTH] Error in login: {type(e).__name__}: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def logout(self):
        """Logout user"""
        self.username = None
        self.token = None
        self.user_id = None
        self.crypto_handler = CryptoHandler()
        self.is_authenticated = False
    
    def get_auth_header(self) -> dict:
        """Get authorization header for API requests"""
        if not self.token:
            return {}
        return {'Authorization': f'Bearer {self.token}'}
    
    def get_public_key(self) -> Optional[str]:
        """Get user's public key"""
        try:
            return self.key_manager.get_public_key()
        except FileNotFoundError:
            return None
