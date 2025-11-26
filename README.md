# CSC-455-Homelab-Project-Cloud

    While this project was ambitiously intended to become a real
    app served on my homelab, it has proven to be a networking nightmare
    (probably because I wrote it). Although functionality is the main focus,
    I wish I had more networking expertise. You can run this project locally
    on a single PC. just run `start_server.bat` and `start_client.bat` to
    experiment with encrypted files. Note that both file names *and* file
    contents are encrypted; however, hashes are stored server-side. 
    Meaning, as long as a user logs in with the correct credentials, their 
    *file names, structure, and integrity* are all preserved.

    Feel free to explore the settings for a dark mode UI,
    and try uploading and downloading files to see how it works!


## Features

- **Client-Side Encryption**: AES-256-GCM encryption with RSA-2048 key management
- **Encrypted Architecture**: Server never sees plaintext data
- **User Authentication**: JWT-based authentication with bcrypt password hashing
- **GUI Interface**: User-friendly Tkinter desktop application
- **Version Control**: Automatic versioning of file updates
- **File Sharing**: Secure file sharing between users
- **Audit Trail**: Complete logging of all operations

## Security

- All files encrypted with AES-256-GCM before upload
- Private keys never leave the client
- Authentication tags prevent tampering
- Rate limiting and session management
- Protection against OWASP Top 10 vulnerabilities

## Installation

1. Clone the repository
2. Create virtual environment:
   ```cmd
   python -m venv venv
   venv\Scripts\activate  # Windows
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Copy `.env.example` to `.env` and configure

5. Initialize database:
   ```bash
   python -m server.app init-db
   ```

## Usage

### Start Server
```bash
python -m server.app
```

### Start Client GUI
```bash
python -m client.gui.main_window
```

## Architecture

```
Client (Tkinter GUI)
    ↓ Encrypts files with AES-256-GCM
    ↓ RSA for key exchange
Server (Flask REST API)
    ↓ Stores encrypted blobs
Database (SQLite/PostgreSQL)
    ↓ Stores metadata only
```

## Development

Run tests:
```bash
pytest tests/
```

## Deployment

### For Homelab/Production Deployment (not yet...)
