"""Basic tests for encryption"""
import sys
from pathlib import Path
import os

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from client.crypto_handler import CryptoHandler, KeyManager
from server.auth import hash_password, verify_password


def test_password_hashing():
    """Test password hashing"""
    print("Testing password hashing...")
    password = "TestPassword123!"
    password_hash, salt = hash_password(password)
    
    assert verify_password(password, password_hash), "Password verification failed"
    assert not verify_password("WrongPassword", password_hash), "Wrong password accepted"
    print("✓ Password hashing test passed")


def test_rsa_keypair():
    """Test RSA key pair generation"""
    print("Testing RSA key pair generation...")
    crypto = CryptoHandler()
    private_key, public_key = crypto.generate_rsa_keypair()
    
    assert private_key and public_key, "Key generation failed"
    assert "BEGIN RSA PRIVATE KEY" in private_key, "Invalid private key format"
    assert "BEGIN PUBLIC KEY" in public_key, "Invalid public key format"
    print("✓ RSA key pair test passed")


def test_string_encryption():
    """Test string encryption and decryption"""
    print("Testing string encryption...")
    crypto = CryptoHandler()
    crypto.generate_rsa_keypair()
    
    original = "Test string for encryption"
    encrypted, iv, tag = crypto.encrypt_string(original)
    decrypted = crypto.decrypt_string(encrypted, iv, tag)
    
    assert decrypted == original, "String decryption failed"
    print("✓ String encryption test passed")


def test_file_encryption():
    """Test file encryption and decryption"""
    print("Testing file encryption...")
    
    # Create test file
    test_file = Path("test_file.txt")
    test_content = b"This is a test file for encryption"
    test_file.write_bytes(test_content)
    
    try:
        crypto = CryptoHandler()
        crypto.generate_rsa_keypair()
        
        # Encrypt
        encrypted_data, metadata = crypto.encrypt_file(str(test_file))
        assert encrypted_data, "Encryption failed"
        assert metadata.get('encrypted_key'), "No encrypted key in metadata"
        
        # Decrypt
        decrypted_data = crypto.decrypt_file(encrypted_data, metadata)
        assert decrypted_data == test_content, "Decryption failed"
        
        print("✓ File encryption test passed")
    finally:
        test_file.unlink(missing_ok=True)


def test_key_manager():
    """Test key manager"""
    print("Testing key manager...")
    
    import tempfile
    with tempfile.TemporaryDirectory() as tmpdir:
        key_manager = KeyManager(Path(tmpdir))
        
        # Generate and save keys
        crypto = CryptoHandler()
        private_key, public_key = crypto.generate_rsa_keypair()
        password = "TestPassword123!"
        
        key_manager.save_keys(private_key, public_key, password)
        
        # Load keys
        loaded_private, loaded_public = key_manager.load_keys(password)
        
        assert loaded_private == private_key, "Private key mismatch"
        assert loaded_public == public_key, "Public key mismatch"
        
        print("✓ Key manager test passed")


def run_all_tests():
    """Run all tests"""
    print("\n" + "="*50)
    print("Running Encryption Tests")
    print("="*50 + "\n")
    
    try:
        test_password_hashing()
        test_rsa_keypair()
        test_string_encryption()
        test_file_encryption()
        test_key_manager()
        
        print("\n" + "="*50)
        print("✓ All tests passed!")
        print("="*50 + "\n")
        return True
    except AssertionError as e:
        print(f"\n✗ Test failed: {e}")
        return False
    except Exception as e:
        print(f"\n✗ Error running tests: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == '__main__':
    run_all_tests()
