# Deployment Files

This folder contains everything you need to deploy the Cloud Storage application.

## Quick Reference

### For Building Windows Executables:

**Client (for users):**
```bash
.\deployment\build_client.bat
```
Output: `dist\CloudStorageClient.exe` - Give this to users!

**Server (if running on Windows):**
```bash
.\deployment\build_server.bat
```
Output: `dist\CloudStorageServer.exe`

### For Proxmox/Linux Deployment:

**Using Docker (Recommended):**
```bash
# On your Proxmox VM
docker-compose up -d
```

**Using Systemd Service:**
```bash
# Install the service
sudo cp deployment/cloud-storage-server.service /etc/systemd/system/
sudo systemctl enable cloud-storage-server
sudo systemctl start cloud-storage-server
```

## Files Explained

### Build Scripts
- `build_client.bat` - Builds Windows executable for client
- `build_server.bat` - Builds Windows executable for server

### PyInstaller Specs
- `client.spec` - Configuration for client executable
- `server.spec` - Configuration for server executable

### Linux/Proxmox Deployment
- `cloud-storage-server.service` - Systemd service file
- `nginx-config` - Nginx reverse proxy configuration
- `.env.template` - Environment variables template

### Docker Files (in root)
- `Dockerfile` - Container definition
- `docker-compose.yml` - Docker Compose configuration

## Need Help?

See the main `DEPLOYMENT.md` file in the project root for complete instructions!
