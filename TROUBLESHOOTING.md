# Troubleshooting Guide - CSC-455-Homelab-Project-Cloud

## Common Issues and Solutions

### 1. Connection Errors

#### "Could not connect to server"

**Symptoms:**
- Login fails with connection error
- "Check Server Connection" button shows offline
- Error: "Could not connect to server. Please check if the server is running and try again."

**Solutions:**

**Step 1: Check if server is running**
```powershell
# Look for a terminal window with Flask server output
# You should see: "Running on http://127.0.0.1:5000"
```

**Step 2: Start the server if not running**
```powershell
.\start_server.bat
```
Or manually:
```powershell
.\venv\Scripts\activate
python -m server.app
```

**Step 3: Verify server is listening**
- Open browser and go to: http://127.0.0.1:5000/api/health
- Should see: `{"message": "Server is running", "status": "success"}`

**Step 4: Check firewall**
- Windows Firewall may block Python
- Allow Python through firewall when prompted
- Or temporarily disable firewall for testing

**Step 5: Check port availability**
```powershell
netstat -ano | findstr :5000
```
- If port 5000 is in use by another application, change port in `config.yaml`

---

### 2. Authentication Errors (401)

#### "Authentication failed" or "Session expired"

**Symptoms:**
- Login fails with 401 error
- Operations fail with "Your session has expired"
- Error dialog: "Authentication failed. Please check your credentials or login again."

**Solutions:**

**For Login Failures:**
1. **Verify credentials**
   - Username is case-sensitive
   - Password must match exactly
   - Check Caps Lock is off

2. **Check if account exists**
   - Try registering if new user
   - Username must be unique

3. **Server connection**
   - Use "Check Server Connection" button
   - Ensure server is running

**For Session Expiry:**
1. **Token expired (after 24 hours)**
   - Simply logout and login again
   - Tokens expire for security

2. **Server restarted**
   - If server restarts, all sessions are invalidated
   - Logout and login again

3. **Database reset**
   - If database was deleted, re-register account
   - Your encrypted files may be lost

---

### 3. Upload Errors

#### "Upload failed" or "File too large"

**Symptoms:**
- Upload gets stuck at "Encrypting and uploading..."
- Error: "File too large. Maximum file size is 100MB."
- Status bar shows error after upload attempt

**Solutions:**

**File Too Large (413 error):**
```
Maximum file size: 100 MB
```
- Compress file before uploading
- Split large files into smaller parts
- Or increase limit in `config.yaml`:
  ```yaml
  storage:
    max_file_size: 209715200  # 200MB
  ```

**Storage Quota Exceeded (413 error):**
```
Default quota: 1 GB per user
```
- Delete old files to free space
- Check storage usage in top-right of window
- Or increase quota in `config.yaml`:
  ```yaml
  storage:
    user_quota: 2147483648  # 2GB
  ```

**Network Timeout:**
- Large files may timeout on slow connections
- Increase timeout in `client/api_client.py`:
  ```python
  self.timeout = 60  # Increase from 30 to 60 seconds
  ```

**Encryption Error:**
- File may be corrupted
- Insufficient disk space
- Try a different file
- Check client logs for details

---

### 4. Download Errors

#### "Download failed" or "File not found"

**Symptoms:**
- Download fails with error
- File appears in list but won't download
- Error: "Failed to download file"

**Solutions:**

**File Not Found (404):**
- File may have been deleted
- Database and storage out of sync
- Refresh file list to update

**Decryption Error:**
- Keys may be corrupted
- Wrong password used at login
- Try logging out and back in

**Network Error:**
- Connection lost during download
- Server may have crashed
- Try again after checking server

---

### 5. Key Management Errors

#### "Error loading encryption keys"

**Symptoms:**
- Login succeeds but key loading fails
- Can't encrypt/decrypt files
- Error: "Could not load encryption keys"

**Solutions:**

**First Login:**
- Keys are generated automatically
- This is normal, just wait a moment

**Password Mismatch:**
- Keys are encrypted with your password
- Must use same password as registration
- If forgotten, keys are unrecoverable

**Corrupted Keys:**
```
Key location: C:\Users\<YourName>\.csc455_homelab\keys\
```
- Delete `.csc455_homelab` folder
- Register new account
- Old encrypted files will be inaccessible

**Regenerate Keys:**
```powershell
# Delete key directory
Remove-Item -Recurse -Force ~/.csc455_homelab

# Login will generate new keys
# Note: You won't be able to decrypt old files
```

---

### 6. GUI Issues

#### Window doesn't appear or crashes

**Symptoms:**
- Client starts but no window appears
- Client crashes immediately
- Python errors in console

**Solutions:**

**Missing Dependencies:**
```powershell
# Reinstall all dependencies
.\venv\Scripts\pip install -r requirements.txt --force-reinstall
```

**Tkinter Not Installed:**
```powershell
# Tkinter should come with Python
# If missing, reinstall Python with "tcl/tk" option checked
```

**Display Issues:**
- Try running from terminal to see errors
- Check Python version: `python --version` (need 3.7+)
- Update graphics drivers

---

### 7. Server Errors (500)

#### "Server error" or "Internal server error"

**Symptoms:**
- Operations fail with 500 error
- Server console shows Python errors
- Error: "Server error. Please try again later."

**Solutions:**

**Check Server Logs:**
- Look at server terminal for error details
- Usually shows Python traceback

**Common Server Issues:**

1. **Database locked:**
   ```
   sqlite3.OperationalError: database is locked
   ```
   - Close other connections to database
   - Use PostgreSQL for production

2. **Missing dependencies:**
   ```powershell
   .\venv\Scripts\pip install -r requirements.txt
   ```

3. **Corrupt database:**
   ```powershell
   # Backup first!
   del csc455_homelab.db
   # Restart server to recreate
   ```

4. **Disk full:**
   - Check disk space
   - Clean up uploads folder
   - Delete old file versions

---

### 8. Performance Issues

#### Slow uploads/downloads or UI freezes

**Symptoms:**
- Operations take very long
- UI becomes unresponsive
- Progress bars don't update

**Solutions:**

**Large File Performance:**
- Encryption is CPU-intensive
- Large files (>50MB) take longer
- Consider splitting files

**Increase Chunk Size:**
Edit `shared/constants.py`:
```python
CHUNK_SIZE = 16 * 1024 * 1024  # 16MB instead of 8MB
```

**Use SSD:**
- Encryption/decryption faster on SSD
- Move uploads folder to SSD

**Close Other Programs:**
- Free up CPU and memory
- Antivirus may slow encryption

---

## Diagnostic Commands

### Check Server Status
```powershell
# Test server health
curl http://127.0.0.1:5000/api/health
```

### Check Database
```powershell
# View database
sqlite3 csc455_homelab.db
.tables
SELECT * FROM users;
.quit
```

### Check Python Environment
```powershell
# Verify Python version
python --version

# Check installed packages
pip list

# Verify key packages
pip show pycryptodome flask
```

### Check Network
```powershell
# Test local connection
ping 127.0.0.1

# Check if port is open
netstat -ano | findstr :5000
```

### View Logs
```powershell
# Server logs (in server terminal)
# Look for error messages, tracebacks

# Client errors
# Run client from terminal to see output:
python -m client.gui.main_window
```

---

## Error Messages Reference

### Client Error Messages

| Error Message | Cause | Solution |
|--------------|-------|----------|
| "Could not connect to server" | Server not running | Start server |
| "Authentication failed" | Wrong credentials | Check username/password |
| "Your session has expired" | Token expired (>24h) | Logout and login |
| "File too large" | File > 100MB | Use smaller file |
| "Storage quota exceeded" | Used > 1GB | Delete old files |
| "Request timed out" | Network/server slow | Try again, increase timeout |
| "Error loading encryption keys" | Key file corrupted | Regenerate keys |
| "File not found" | File deleted | Refresh file list |

### Server Error Messages

| Status Code | Meaning | Common Cause |
|------------|---------|--------------|
| 400 | Bad Request | Invalid data sent |
| 401 | Unauthorized | Token expired/invalid |
| 403 | Forbidden | No permission |
| 404 | Not Found | File doesn't exist |
| 413 | Payload Too Large | File/quota limit |
| 500 | Internal Error | Server bug/crash |

---

## Advanced Troubleshooting

### Enable Debug Mode

**Server:**
Edit `config.yaml`:
```yaml
server:
  debug: true
```

**Client:**
Add prints in code or run with verbose output

### Reset Everything

**Complete Clean Reset:**
```powershell
# Stop server (Ctrl+C)

# Delete database
del csc455_homelab.db

# Delete uploaded files
Remove-Item -Recurse -Force uploads\*

# Delete client keys
Remove-Item -Recurse -Force $env:USERPROFILE\.csc455_homelab

# Restart server
python -m server.app

# Register new account in client
```

### Common Python Errors

**ImportError: No module named 'X'**
```powershell
.\venv\Scripts\pip install <module>
```

**ModuleNotFoundError: No module named 'server'**
```powershell
# Make sure you're in project directory
cd C:\Users\Ty\455-proj
```

**Permission Error: [WinError 5]**
```powershell
# Run as administrator or check file permissions
```

---

## Getting Help

### Information to Provide

When reporting issues, include:

1. **Error message** (full text)
2. **Steps to reproduce**
3. **Server logs** (from terminal)
4. **Python version**: `python --version`
5. **Operating system**
6. **When it started** (after what action)

### Check Logs

**Server logs:**
- Visible in server terminal
- Shows all API requests and errors

**Client behavior:**
- Error dialogs show user-friendly messages
- Run client from terminal for detailed output

### Test Components

**Test Encryption:**
```powershell
python tests\test_crypto.py
```

**Test Server API:**
```powershell
# In Python:
from client.api_client import APIClient
api = APIClient("http://127.0.0.1:5000")
print(api.health_check())  # Should return True
```

---

## Prevention Tips

1. **Keep server running** while using client
2. **Regular backups** of database and uploads folder
3. **Don't delete** `.csc455_homelab` folder (contains keys)
4. **Remember password** - keys can't be recovered
5. **Monitor storage** usage to avoid quota issues
6. **Update dependencies** regularly
7. **Use strong passwords** (12+ chars, mixed)
8. **Test with small files** first before large uploads

---

## Still Having Issues?

1. Check `QUICKSTART.md` for setup instructions
2. Review `IMPLEMENTATION_PLAN.md` for architecture details
3. Run `python tests\test_crypto.py` to verify encryption
4. Check server terminal for detailed error messages
5. Try with a fresh virtual environment
6. Review this troubleshooting guide section by section

---

**Last Updated:** November 26, 2025
**System Version:** 1.0.0
