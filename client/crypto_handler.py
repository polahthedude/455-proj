"""Cryptographic operations for client-side encryption"""
import os
import hashlib
from pathlib import Path
from typing import Tuple
from Crypto.Cipher import AES
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_OAEP
from Crypto.Random import get_random_bytes
from Crypto.Protocol.KDF import PBKDF2
from shared.constants import (
    AES_KEY_SIZE, AES_BLOCK_SIZE, RSA_KEY_SIZE,
    CHUNK_SIZE, PBKDF2_ITERATIONS
)


class CryptoHandler:
    """Handles all cryptographic operations"""
    
    def __init__(self):
        self.private_key = None
        self.public_key = None
        self.rsa_cipher = None
    
    # ==================== Key Management ====================
    
    def generate_rsa_keypair(self) -> Tuple[str, str]:
        """Generate RSA-2048 key pair"""
        key = RSA.generate(RSA_KEY_SIZE)
        private_key = key.export_key()
        public_key = key.publickey().export_key()
        
        self.private_key = key
        self.public_key = key.publickey()
        self.rsa_cipher = PKCS1_OAEP.new(self.private_key)
        
        return private_key.decode('utf-8'), public_key.decode('utf-8')
    
    def load_private_key(self, private_key_pem: str, passphrase: str = None):
        """Load private key from PEM format"""
        if passphrase:
            passphrase = passphrase.encode('utf-8')
        
        self.private_key = RSA.import_key(private_key_pem, passphrase=passphrase)
        self.rsa_cipher = PKCS1_OAEP.new(self.private_key)
        self.public_key = self.private_key.publickey()
    
    def load_public_key(self, public_key_pem: str):
        """Load public key from PEM format"""
        self.public_key = RSA.import_key(public_key_pem)
    
    def encrypt_private_key(self, private_key_pem: str, password: str) -> bytes:
        """Encrypt private key with password-derived key"""
        salt = get_random_bytes(16)
        key = PBKDF2(password, salt, dkLen=AES_KEY_SIZE, count=PBKDF2_ITERATIONS)
        
        cipher = AES.new(key, AES.MODE_GCM)
        ciphertext, tag = cipher.encrypt_and_digest(private_key_pem.encode('utf-8'))
        
        # Return salt + nonce + tag + ciphertext
        return salt + cipher.nonce + tag + ciphertext
    
    def decrypt_private_key(self, encrypted_data: bytes, password: str) -> str:
        """Decrypt private key with password-derived key"""
        salt = encrypted_data[:16]
        nonce = encrypted_data[16:32]
        tag = encrypted_data[32:48]
        ciphertext = encrypted_data[48:]
        
        key = PBKDF2(password, salt, dkLen=AES_KEY_SIZE, count=PBKDF2_ITERATIONS)
        
        cipher = AES.new(key, AES.MODE_GCM, nonce=nonce)
        private_key_pem = cipher.decrypt_and_verify(ciphertext, tag)
        
        return private_key_pem.decode('utf-8')
    
    # ==================== File Encryption ====================
    
    def encrypt_file(self, file_path: str) -> Tuple[bytes, dict]:
        """
        Encrypt file with AES-256-GCM
        Returns: (encrypted_data, metadata)
        """
        # Generate random AES key and IV
        aes_key = get_random_bytes(AES_KEY_SIZE)
        
        # Read and encrypt file in chunks
        encrypted_chunks = []
        cipher = AES.new(aes_key, AES.MODE_GCM)
        
        with open(file_path, 'rb') as f:
            while True:
                chunk = f.read(CHUNK_SIZE)
                if not chunk:
                    break
                encrypted_chunks.append(cipher.encrypt(chunk))
        
        # Get authentication tag
        tag = cipher.digest()
        
        # Combine all encrypted data
        encrypted_data = b''.join(encrypted_chunks)
        
        # Encrypt AES key with RSA public key
        if not self.public_key:
            raise ValueError("Public key not loaded")
        
        rsa_cipher = PKCS1_OAEP.new(self.public_key)
        encrypted_aes_key = rsa_cipher.encrypt(aes_key)
        
        # Calculate file hash
        file_hash = hashlib.sha256(encrypted_data).hexdigest()
        
        metadata = {
            'encrypted_key': encrypted_aes_key.hex(),
            'iv': cipher.nonce.hex(),
            'auth_tag': tag.hex(),
            'file_hash': file_hash
        }
        
        return encrypted_data, metadata
    
    def decrypt_file(self, encrypted_data: bytes, metadata: dict) -> bytes:
        """
        Decrypt file with AES-256-GCM
        """
        # Decrypt AES key with RSA private key
        if not self.rsa_cipher:
            raise ValueError("Private key not loaded")
        
        encrypted_aes_key = bytes.fromhex(metadata['encrypted_key'])
        aes_key = self.rsa_cipher.decrypt(encrypted_aes_key)
        
        # Get IV and tag
        iv = bytes.fromhex(metadata['iv'])
        tag = bytes.fromhex(metadata['auth_tag'])
        
        # Decrypt data
        cipher = AES.new(aes_key, AES.MODE_GCM, nonce=iv)
        
        try:
            decrypted_data = cipher.decrypt_and_verify(encrypted_data, tag)
        except ValueError as e:
            raise ValueError("Authentication failed - file may be corrupted or tampered with")
        
        return decrypted_data
    
    # ==================== String Encryption ====================
    
    def encrypt_string(self, plaintext: str) -> Tuple[str, str, str]:
        """
        Encrypt string with AES-256-GCM
        Returns: (ciphertext_hex, iv_hex, tag_hex)
        """
        aes_key = get_random_bytes(AES_KEY_SIZE)
        cipher = AES.new(aes_key, AES.MODE_GCM)
        
        ciphertext, tag = cipher.encrypt_and_digest(plaintext.encode('utf-8'))
        
        # Encrypt AES key with RSA
        rsa_cipher = PKCS1_OAEP.new(self.public_key)
        encrypted_key = rsa_cipher.encrypt(aes_key)
        
        return (
            encrypted_key.hex() + ':' + ciphertext.hex(),
            cipher.nonce.hex(),
            tag.hex()
        )
    
    def decrypt_string(self, encrypted_data: str, iv_hex: str, tag_hex: str) -> str:
        """
        Decrypt string with AES-256-GCM
        """
        # Split encrypted key and ciphertext
        encrypted_key_hex, ciphertext_hex = encrypted_data.split(':', 1)
        encrypted_key = bytes.fromhex(encrypted_key_hex)
        ciphertext = bytes.fromhex(ciphertext_hex)
        
        # Decrypt AES key
        aes_key = self.rsa_cipher.decrypt(encrypted_key)
        
        # Decrypt data
        iv = bytes.fromhex(iv_hex)
        tag = bytes.fromhex(tag_hex)
        
        cipher = AES.new(aes_key, AES.MODE_GCM, nonce=iv)
        plaintext = cipher.decrypt_and_verify(ciphertext, tag)
        
        return plaintext.decode('utf-8')
    
    # ==================== Utility Functions ====================
    
    @staticmethod
    def hash_file(file_path: str) -> str:
        """Calculate SHA-256 hash of file"""
        sha256_hash = hashlib.sha256()
        
        with open(file_path, 'rb') as f:
            for chunk in iter(lambda: f.read(CHUNK_SIZE), b''):
                sha256_hash.update(chunk)
        
        return sha256_hash.hexdigest()
    
    @staticmethod
    def hash_data(data: bytes) -> str:
        """Calculate SHA-256 hash of data"""
        return hashlib.sha256(data).hexdigest()


class KeyManager:
    """Manages key storage and retrieval"""
    
    def __init__(self, keys_dir: Path = None):
        if keys_dir is None:
            keys_dir = Path.home() / '.csc455_homelab' / 'keys'
        
        self.keys_dir = Path(keys_dir)
        self.keys_dir.mkdir(parents=True, exist_ok=True)
        
        self.private_key_path = self.keys_dir / 'private_key.enc'
        self.public_key_path = self.keys_dir / 'public_key.pem'
    
    def save_keys(self, private_key_pem: str, public_key_pem: str, password: str):
        """Save encrypted private key and public key"""
        crypto = CryptoHandler()
        encrypted_private = crypto.encrypt_private_key(private_key_pem, password)
        
        # Save encrypted private key
        with open(self.private_key_path, 'wb') as f:
            f.write(encrypted_private)
        
        # Save public key
        with open(self.public_key_path, 'w') as f:
            f.write(public_key_pem)
    
    def load_keys(self, password: str) -> Tuple[str, str]:
        """Load and decrypt keys"""
        if not self.private_key_path.exists():
            raise FileNotFoundError("Private key not found")
        
        # Load encrypted private key
        with open(self.private_key_path, 'rb') as f:
            encrypted_private = f.read()
        
        # Decrypt private key
        crypto = CryptoHandler()
        private_key_pem = crypto.decrypt_private_key(encrypted_private, password)
        
        # Load public key
        with open(self.public_key_path, 'r') as f:
            public_key_pem = f.read()
        
        return private_key_pem, public_key_pem
    
    def keys_exist(self) -> bool:
        """Check if keys exist"""
        return self.private_key_path.exists() and self.public_key_path.exists()
    
    def get_public_key(self) -> str:
        """Get public key without password"""
        if not self.public_key_path.exists():
            raise FileNotFoundError("Public key not found")
        
        with open(self.public_key_path, 'r') as f:
            return f.read()
