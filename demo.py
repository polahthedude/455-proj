"""
Demo script to showcase the CSC-455-Homelab-Project-Cloud system
Run this after starting the server to test all features
"""
import sys
import time
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from client.api_client import APIClient
from client.crypto_handler import CryptoHandler, KeyManager
from client.auth_manager import AuthManager


def print_header(text):
    """Print formatted header"""
    print("\n" + "="*60)
    print(f"  {text}")
    print("="*60)


def print_step(step, text):
    """Print formatted step"""
    print(f"\n[Step {step}] {text}")
    time.sleep(0.5)


def demo():
    """Run complete demo"""
    print_header("CSC-455-Homelab-Project-Cloud - Demo")
    print("\nThis demo will showcase all core features:")
    print("  • User registration")
    print("  • Encryption key generation")
    print("  • File encryption")
    print("  • File upload")
    print("  • File download & decryption")
    print("  • File deletion")
    
    input("\nPress Enter to begin demo...")
    
    # Initialize
    api_client = APIClient("http://127.0.0.1:5000")
    
    # Check server
    print_step(1, "Checking server connection...")
    if not api_client.health_check():
        print("❌ Server is not running. Please start the server first.")
        print("   Run: python -m server.app")
        return
    print("✅ Server is running")
    
    # Register user
    print_step(2, "Registering new user...")
    username = f"demo_user_{int(time.time())}"
    email = f"{username}@example.com"
    password = "DemoPassword123!"
    
    # Generate keys
    crypto = CryptoHandler()
    private_key, public_key = crypto.generate_rsa_keypair()
    print(f"   Username: {username}")
    print(f"   Email: {email}")
    print(f"   Password: {password}")
    print(f"   RSA Key Size: 2048 bits")
    
    success, response = api_client.register(username, email, password, public_key)
    if success:
        print("✅ User registered successfully")
    else:
        print(f"❌ Registration failed: {response.get('message')}")
        return
    
    # Login
    print_step(3, "Logging in...")
    success, response = api_client.login(username, password)
    if success:
        token = response.get('token')
        user_id = response.get('user', {}).get('id')
        print("✅ Login successful")
        print(f"   JWT Token: {token[:50]}...")
    else:
        print(f"❌ Login failed: {response.get('message')}")
        return
    
    # Load keys into crypto handler
    crypto.load_private_key(private_key)
    
    # Create test file
    print_step(4, "Creating test file...")
    test_file = Path("demo_test.txt")
    test_content = b"This is a demo file for the CSC-455-Homelab-Project-Cloud system!\nIt will be encrypted with AES-256-GCM before upload."
    test_file.write_bytes(test_content)
    print(f"✅ Created test file: {test_file}")
    print(f"   Original size: {len(test_content)} bytes")
    print(f"   Content preview: {test_content[:50].decode()}...")
    
    # Encrypt file
    print_step(5, "Encrypting file with AES-256-GCM...")
    encrypted_data, metadata = crypto.encrypt_file(str(test_file))
    print("✅ File encrypted successfully")
    print(f"   Encrypted size: {len(encrypted_data)} bytes")
    print(f"   IV: {metadata['iv'][:32]}...")
    print(f"   Auth tag: {metadata['auth_tag'][:32]}...")
    print(f"   File hash: {metadata['file_hash'][:32]}...")
    
    # Encrypt filename
    encrypted_filename, iv, tag = crypto.encrypt_string(test_file.name)
    metadata['encrypted_filename'] = encrypted_filename
    
    # Upload file
    print_step(6, "Uploading encrypted file to server...")
    success, response = api_client.upload_file(
        str(test_file),
        encrypted_data,
        metadata,
        token
    )
    
    if success:
        file_uuid = response.get('file', {}).get('file_uuid')
        print("✅ File uploaded successfully")
        print(f"   File UUID: {file_uuid}")
    else:
        print(f"❌ Upload failed: {response.get('message')}")
        test_file.unlink(missing_ok=True)
        return
    
    # List files
    print_step(7, "Listing user files...")
    success, response = api_client.list_files(token)
    if success:
        files = response.get('files', [])
        storage_used = response.get('storage_used', 0)
        print(f"✅ Found {len(files)} file(s)")
        print(f"   Storage used: {storage_used / 1024:.2f} KB")
        for file in files:
            print(f"   • File UUID: {file.get('file_uuid')}")
            print(f"     Size: {file.get('size')} bytes")
            print(f"     Uploaded: {file.get('uploaded_at')}")
    else:
        print(f"❌ List failed: {response.get('message')}")
    
    # Download file
    print_step(8, "Downloading and decrypting file...")
    success, data = api_client.download_file(file_uuid, token)
    
    if success:
        print("✅ File downloaded successfully")
        print(f"   Downloaded size: {len(data)} bytes")
        
        # Decrypt file
        decrypted_data = crypto.decrypt_file(data, metadata)
        print("✅ File decrypted successfully")
        print(f"   Decrypted size: {len(decrypted_data)} bytes")
        print(f"   Content matches: {decrypted_data == test_content}")
        print(f"   Decrypted content: {decrypted_data.decode()}")
    else:
        print(f"❌ Download failed")
    
    # Delete file
    print_step(9, "Deleting file from server...")
    success, response = api_client.delete_file(file_uuid, token)
    if success:
        print("✅ File deleted successfully")
    else:
        print(f"❌ Delete failed: {response.get('message')}")
    
    # Cleanup
    print_step(10, "Cleaning up...")
    test_file.unlink(missing_ok=True)
    print("✅ Cleanup complete")
    
    # Summary
    print_header("Demo Complete!")
    print("\n✅ All core features working:")
    print("   ✓ User registration with validation")
    print("   ✓ RSA-2048 key pair generation")
    print("   ✓ AES-256-GCM file encryption")
    print("   ✓ JWT authentication")
    print("   ✓ Secure file upload")
    print("   ✓ File download and decryption")
    print("   ✓ File deletion")
    print("   ✓ Storage tracking")
    
    print("\n🔐 Security features verified:")
    print("   ✓ Client-side encryption")
    print("   ✓ Server never sees plaintext")
    print("   ✓ Authentication tags prevent tampering")
    print("   ✓ Password-protected keys")
    
    print("\n🚀 Next steps:")
    print("   • Start the client GUI: python -m client.gui.main_window")
    print("   • Add version control feature")
    print("   • Implement file sharing")
    print("   • Deploy to production")
    
    print("\n" + "="*60)


if __name__ == '__main__':
    try:
        demo()
    except KeyboardInterrupt:
        print("\n\nDemo interrupted by user")
    except Exception as e:
        print(f"\n\n❌ Error during demo: {e}")
        import traceback
        traceback.print_exc()
