# CSC-455-Homelab-Project-Cloud - Quick Start Guide

## Installation

### 1. Create Virtual Environment
```powershell
python -m venv venv
venv\Scripts\activate
```

### 2. Install Dependencies
```powershell
pip install -r requirements.txt
```

### 3. Configure Environment
Copy `.env.example` to `.env` and configure if needed:
```powershell
copy .env.example .env
```

The default configuration works for local development.

## Running the Application

### Option 1: Using Batch Files (Windows)

**Start Server:**
```powershell
.\start_server.bat
```

**Start Client (in a new terminal):**
```powershell
.\start_client.bat
```

### Option 2: Manual Start

**Start Server:**
```powershell
python -m server.app
```

**Start Client:**
```powershell
python -m client.gui.main_window
```

## First Time Setup

1. **Start the server** first and wait for "Running on http://127.0.0.1:5000"

2. **Start the client** - the login dialog will appear

3. **Register a new account**:
   - Click the "Register" tab
   - Enter username (minimum 3 characters)
   - Enter email address
   - Create a strong password (min 12 chars, mixed case, numbers, special chars)
   - Confirm password
   - Click "Register"

4. **Login**:
   - Switch to "Login" tab
   - Enter your credentials
   - Click "Login"

5. **Upload files**:
   - Click "📁 Upload File"
   - Select a file
   - File will be encrypted and uploaded automatically

6. **Download files**:
   - Select a file from the list
   - Click "📥 Download" or double-click the file
   - Choose where to save
   - File will be downloaded and decrypted automatically

## Features

### ✓ Implemented
- ✅ User registration and login
- ✅ AES-256-GCM file encryption
- ✅ RSA-2048 key management
- ✅ File upload/download
- ✅ File deletion
- ✅ Storage quota tracking
- ✅ GUI interface
- ✅ JWT authentication

### 🚧 Optional Features (To Be Added)
- ⏳ File versioning
- ⏳ File sharing between users
- ⏳ Search and filtering
- ⏳ File metadata encryption display

## Architecture

```
┌──────────────┐
│    Client    │  → Encrypts files with AES-256-GCM
│  (Tkinter)   │  → RSA-2048 for key exchange
└──────┬───────┘
       │ HTTPS
       ↓
┌──────────────┐
│    Server    │  → Stores encrypted blobs only
│   (Flask)    │  → JWT authentication
└──────┬───────┘
       │
       ↓
┌──────────────┐
│   Database   │  → Metadata only (no plaintext)
│   (SQLite)   │
└──────────────┘
```

## Security Features

- **Zero-Knowledge**: Server never sees plaintext data
- **Client-Side Encryption**: All encryption happens on client
- **Strong Encryption**: AES-256-GCM with authentication
- **Secure Key Exchange**: RSA-2048 for key encryption
- **Password Protection**: Bcrypt with salt
- **JWT Authentication**: Token-based sessions

## Troubleshooting

### Server won't start
- Check if port 5000 is already in use
- Make sure all dependencies are installed
- Check for errors in the console

### Can't login
- Make sure server is running
- Check username and password
- Try registering a new account

### Upload fails
- Check file size (max 100MB)
- Check storage quota (1GB per user)
- Make sure you're logged in

### Download fails
- File may be corrupted
- Check encryption keys are loaded correctly
- Try refreshing the file list

## Testing

Run encryption tests:
```powershell
python tests\test_crypto.py
```

## Project Structure

```
455-proj/
├── client/              # Client-side code
│   ├── gui/            # Tkinter GUI
│   ├── crypto_handler.py   # Encryption logic
│   ├── api_client.py        # API communication
│   └── auth_manager.py      # Authentication
├── server/              # Server-side code
│   ├── app.py          # Flask application
│   ├── auth.py         # Authentication logic
│   ├── models.py       # Database models
│   ├── storage.py      # File storage
│   └── config.py       # Configuration
├── shared/             # Shared constants
├── tests/              # Test suite
├── uploads/            # Encrypted file storage
├── config.yaml         # Configuration
└── requirements.txt    # Dependencies
```

## Development

### Add New Features
1. Update models in `server/models.py` if needed
2. Add API endpoints in `server/app.py`
3. Update client in `client/api_client.py`
4. Update GUI in `client/gui/`

### Database Migrations
To reset database:
```powershell
del csc455_homelab.db
python -m server.app
```

## License

MIT License - See project documentation for details.

## Support

For issues or questions, refer to the IMPLEMENTATION_PLAN.md document.
