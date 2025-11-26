# Cloud Storage Client - User Guide

## Quick Start

1. **First Time Setup**
   - Double-click `CloudStorageClient.exe`
   - If needed, edit `config.yaml` to set your server URL
   - The login screen will appear

2. **Login**
   - Enter your username and password
   - Or click "Register" to create a new account

3. **Using the Application**
   - Upload files by clicking "Upload" or dragging files
   - Download files by selecting them and clicking "Download"
   - Create folders to organize your files
   - Files are automatically encrypted before upload

## Configuration

Edit `config.yaml` to change settings:

```yaml
client:
  server_url: "https://your-server-url-here"  # Change this to your server
  keys_directory: ".csc455_homelab/keys"
  cache_directory: ".csc455_homelab/cache"
```

## Features

- **Secure**: End-to-end encryption of your files
- **Easy**: Simple drag-and-drop interface
- **Fast**: Efficient file transfer and caching
- **Organized**: Create folders and manage your files
- **Reliable**: Version control and file integrity checking

## Troubleshooting

### Can't Connect to Server
- Verify the `server_url` in `config.yaml` is correct
- Check your internet connection
- Verify the server is running
- Try accessing the server URL in your web browser

### Login Issues
- Ensure username and password are correct
- Check if server is accessible
- Try registering a new account

### Upload Issues
- Check file size (max 100MB by default)
- Verify you have available storage quota
- Ensure stable internet connection

## Security Notes

- Your files are encrypted before upload
- Your encryption keys are stored locally in `~/.csc455_homelab/keys/`
- Keep your password secure - it cannot be recovered
- **Important**: Backup your keys folder if you format your computer

## Support

For help or issues, contact your system administrator or see the project documentation.

## Technical Details

- **File Encryption**: AES-256-GCM
- **Key Exchange**: RSA-2048
- **Authentication**: JWT tokens
- **Max File Size**: 100MB (configurable by server admin)
- **Storage Quota**: 1GB per user (configurable by server admin)

---

**Version**: 1.0
**Platform**: Windows 10/11
**Requirements**: None - all dependencies included in executable
