"""
Debug script to wipe entire system - USE WITH CAUTION!
This will delete:
- All database data (users, files, folders, shares)
- All uploaded file data
- All client-side encryption keys
- All client-side settings
"""
import os
import sys
import shutil
import subprocess
from pathlib import Path


def kill_server_process():
    """Kill any running Flask server processes"""
    try:
        if sys.platform == 'win32':
            # Windows: Find and kill python processes running the server
            result = subprocess.run(
                ['tasklist', '/FI', 'IMAGENAME eq python.exe', '/FO', 'CSV', '/NH'],
                capture_output=True,
                text=True
            )
            
            # Look for processes with server-related keywords
            killed = False
            for line in result.stdout.strip().split('\n'):
                if line:
                    parts = line.strip('"').split('","')
                    if len(parts) >= 2:
                        pid = parts[1]
                        # Kill the process
                        try:
                            subprocess.run(['taskkill', '/F', '/PID', pid], 
                                         capture_output=True, check=False)
                            killed = True
                        except:
                            pass
            
            if killed:
                print("✓ Stopped server processes")
                import time
                time.sleep(1)  # Wait for processes to fully terminate
        else:
            # Unix-like systems
            subprocess.run(['pkill', '-f', 'flask'], capture_output=True, check=False)
            subprocess.run(['pkill', '-f', 'python.*server'], capture_output=True, check=False)
            print("✓ Stopped server processes")
    except Exception as e:
        print(f"! Could not stop server: {e}")


def wipe_system():
    """Wipe all system data"""
    print("=" * 60)
    print("CSC-455-HOMELAB-PROJECT-CLOUD - SYSTEM WIPE UTILITY")
    print("=" * 60)
    print("\nWARNING: This will delete ALL data:")
    print("  • Server database (ALL USER ACCOUNTS)")
    print("  • All uploaded files")
    print("  • All folders")
    print("  • All file shares")
    print("  • Client encryption keys")
    print("  • Client settings")
    print("\nThe database contains:")
    print("  - User accounts and passwords")
    print("  - File metadata")
    print("  - Folder structure")
    print("  - Sharing permissions")
    print()
    
    response = input("Are you ABSOLUTELY sure? Type 'WIPE' to confirm: ")
    
    if response != "WIPE":
        print("\nAborted. No changes made.")
        return
    
    print("\n" + "=" * 60)
    print("Starting system wipe...")
    print("=" * 60 + "\n")
    
    # First, stop the server
    print("Stopping server processes...")
    kill_server_process()
    print()
    
    # 1. Delete server database (contains all users, files, folders, shares)
    db_path = Path(__file__).parent / 'server' / 'instance' / 'csc455_homelab.db'
    if db_path.exists():
        max_attempts = 3
        for attempt in range(max_attempts):
            try:
                os.remove(db_path)
                print(f"✓ Deleted database (ALL ACCOUNTS): {db_path}")
                print(f"  - All user accounts removed")
                print(f"  - All file metadata removed")
                print(f"  - All folder structures removed")
                print(f"  - All sharing permissions removed")
                break
            except PermissionError as e:
                if attempt < max_attempts - 1:
                    print(f"! Database locked, attempting to force close... (attempt {attempt + 1}/{max_attempts})")
                    kill_server_process()
                    import time
                    time.sleep(1)
                else:
                    print(f"✗ Failed to delete database after {max_attempts} attempts: {e}")
                    print(f"  CRITICAL: Database is locked!")
                    print(f"  Please manually:")
                    print(f"    1. Close ALL Python/server windows")
                    print(f"    2. Check Task Manager for python.exe processes")
                    print(f"    3. Run this script again")
                    return
            except Exception as e:
                print(f"✗ Failed to delete database: {e}")
                return
    else:
        print(f"- Database not found: {db_path}")
    
    # 2. Delete uploaded files
    uploads_path = Path(__file__).parent / 'uploads'
    if uploads_path.exists():
        try:
            shutil.rmtree(uploads_path)
            print(f"✓ Deleted uploads folder: {uploads_path}")
        except Exception as e:
            print(f"✗ Failed to delete uploads: {e}")
    else:
        print(f"- Uploads folder not found: {uploads_path}")
    
    # 3. Delete client encryption keys
    keys_path = Path.home() / '.csc455_homelab' / 'keys'
    if keys_path.exists():
        try:
            shutil.rmtree(keys_path)
            print(f"✓ Deleted encryption keys: {keys_path}")
        except Exception as e:
            print(f"✗ Failed to delete keys: {e}")
    else:
        print(f"- Keys folder not found: {keys_path}")
    
    # 4. Delete client settings
    settings_file = Path.home() / '.csc455_homelab' / 'settings.json'
    if settings_file.exists():
        try:
            os.remove(settings_file)
            print(f"✓ Deleted settings: {settings_file}")
        except Exception as e:
            print(f"✗ Failed to delete settings: {e}")
    else:
        print(f"- Settings file not found: {settings_file}")
    
    # 5. Delete .csc455_homelab folder if empty
    homelab_path = Path.home() / '.csc455_homelab'
    if homelab_path.exists():
        try:
            # Only delete if empty
            if not any(homelab_path.iterdir()):
                homelab_path.rmdir()
                print(f"✓ Deleted .csc455_homelab folder: {homelab_path}")
            else:
                print(f"- .csc455_homelab folder not empty, keeping it")
        except Exception as e:
            print(f"✗ Failed to delete .csc455_homelab folder: {e}")
    
    # 6. Recreate uploads directory
    uploads_path.mkdir(parents=True, exist_ok=True)
    print(f"✓ Recreated uploads folder: {uploads_path}")
    
    # 7. Recreate server instance directory
    instance_path = Path(__file__).parent / 'server' / 'instance'
    instance_path.mkdir(parents=True, exist_ok=True)
    print(f"✓ Recreated instance folder: {instance_path}")
    
    print("\n" + "=" * 60)
    print("SYSTEM WIPE COMPLETE")
    print("=" * 60)
    print("\nAll data has been deleted:")
    print("  ✓ ALL user accounts removed")
    print("  ✓ ALL files and folders deleted")
    print("  ✓ ALL encryption keys wiped")
    print("  ✓ System reset to factory state")
    print("\nNext steps:")
    print("1. Start the server (it will create a fresh database)")
    print("2. Start the client and REGISTER A NEW ACCOUNT")
    print("3. Your old account is gone - you must create a new one")
    print()


if __name__ == '__main__':
    try:
        wipe_system()
    except KeyboardInterrupt:
        print("\n\nAborted by user. No changes made.")
    except Exception as e:
        print(f"\n\nERROR: {e}")
        print("Some data may have been partially deleted.")
