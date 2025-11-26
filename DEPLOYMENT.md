# Deployment Guide - CSC-455-Homelab-Project-Cloud

## Overview

This guide covers deploying the server on Proxmox (your homelab) and packaging the client as a user-friendly executable for Windows users.

---

## Server Deployment on Proxmox

### Option 1: Docker Container (Recommended)

The easiest way to deploy on Proxmox is using Docker in a lightweight Linux VM or LXC container.

#### 1. Create Ubuntu VM/LXC Container in Proxmox

1. Create new Ubuntu 22.04 LTS container/VM
2. Allocate resources (minimum):
   - CPU: 2 cores
   - RAM: 2GB
   - Storage: 20GB + storage for user files
3. Set up static IP or DHCP reservation

#### 2. Install Docker

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Install Docker Compose
sudo apt install docker-compose -y

# Add your user to docker group
sudo usermod -aG docker $USER
newgrp docker
```

#### 3. Deploy the Application

Transfer the entire project to your VM:

```bash
# On your local machine
scp -r c:\Users\Ty\455-proj username@your-vm-ip:/home/username/cloud-storage

# SSH into the VM
ssh username@your-vm-ip
cd /home/username/cloud-storage

# Start the application
docker-compose up -d
```

#### 4. Configure Networking for Cloud Access

##### Internal Network Setup

Edit `/etc/netplan/00-installer-config.yaml` or use Proxmox web interface:

```yaml
network:
  version: 2
  ethernets:
    eth0:
      dhcp4: no
      addresses:
        - 192.168.1.236
      gateway4: 192.168.1.1
      nameservers:
        addresses:
          - 8.8.8.8
          - 8.8.4.4
```

Apply changes:
```bash
sudo netplan apply
```

##### Router Port Forwarding (for external access)

1. Log into your router's admin panel
2. Forward external port 5000 (or custom port) to your VM's IP (192.168.1.100:5000)
3. For HTTPS, forward port 443 to 5000 (requires reverse proxy)

##### Firewall Configuration

```bash
# Allow server port
sudo ufw allow 5000/tcp

# If using reverse proxy with SSL
sudo ufw allow 443/tcp
sudo ufw allow 80/tcp

# Enable firewall
sudo ufw enable
```

---

### Option 2: Systemd Service (Direct Python)

If you prefer running Python directly without Docker:

#### 1. Install Python on VM

```bash
sudo apt update
sudo apt install python3 python3-pip python3-venv -y
```

#### 2. Transfer and Setup Project

```bash
# Transfer project files
scp -r c:\Users\Ty\455-proj username@your-vm-ip:/opt/cloud-storage

# SSH into VM
ssh username@your-vm-ip
cd /opt/cloud-storage

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Set proper permissions
sudo chown -R $USER:$USER /opt/cloud-storage
chmod +x start_server.sh
```

#### 3. Create Systemd Service

The systemd service file is located at `deployment/cloud-storage-server.service`

Install it:

```bash
sudo cp deployment/cloud-storage-server.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable cloud-storage-server
sudo systemctl start cloud-storage-server

# Check status
sudo systemctl status cloud-storage-server

# View logs
sudo journalctl -u cloud-storage-server -f
```

---

## Reverse Proxy with SSL (Production Recommended)

For production use with domain name and HTTPS:

### Using Nginx + Let's Encrypt

```bash
# Install Nginx
sudo apt install nginx certbot python3-certbot-nginx -y

# Create Nginx configuration
sudo nano /etc/nginx/sites-available/cloud-storage
```

Add this configuration:

```nginx
server {
    listen 80;
    server_name yourdomain.com;  # Replace with your domain

    location / {
        proxy_pass http://localhost:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # WebSocket support (if needed later)
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        
        # File upload settings
        client_max_body_size 100M;
    }
}
```

Enable and get SSL certificate:

```bash
sudo ln -s /etc/nginx/sites-available/cloud-storage /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx

# Get SSL certificate (requires domain pointing to your server)
sudo certbot --nginx -d yourdomain.com
```

### Dynamic DNS (for home connections without static IP)

If you don't have a static public IP, use a DDNS service:

- **DuckDNS** (free): https://www.duckdns.org/
- **No-IP** (free tier): https://www.noip.com/
- **Cloudflare** (free with tunnels): https://www.cloudflare.com/

---

## Client Executable Packaging

### Building Windows Executables

We use PyInstaller to create standalone `.exe` files that users can double-click.

#### 1. Install PyInstaller

```powershell
# Activate your virtual environment
.\venv\Scripts\activate

# Install PyInstaller
pip install pyinstaller
```

#### 2. Build the Client Executable

```powershell
# Run the build script
.\deployment\build_client.bat
```

This creates:
- `dist/CloudStorageClient.exe` - Single executable file
- Includes all dependencies and the GUI
- No need for users to install Python

#### 3. Build the Server Executable (Windows)

If you want to run the server on Windows:

```powershell
.\deployment\build_server.bat
```

This creates `dist/CloudStorageServer.exe`

#### 4. Distribute to Users

Simply share the `.exe` file! Users can:
1. Download the executable
2. Double-click to run
3. First run will show login dialog
4. They need to configure the server URL in `config.yaml` or through a settings dialog

---

## Client Configuration for Remote Access

Users need to update `config.yaml` to point to your server:

```yaml
client:
  server_url: "https://yourdomain.com"  # or "http://your-public-ip:5000"
  keys_directory: ".csc455_homelab/keys"
  cache_directory: ".csc455_homelab/cache"
```

### Auto-Configuration (Recommended)

For easier distribution, you can:

1. **Bundle config with executable**: Edit `client.spec` to include your config
2. **Settings dialog**: Add a GUI settings option (I can add this)
3. **Environment variable**: Check `SERVER_URL` environment variable first

---

## Security Best Practices

### For Production Deployment:

1. **Change Default Secret Key**
   ```yaml
   server:
     secret_key: "generate-long-random-string-here"
   ```
   Generate with: `python -c "import secrets; print(secrets.token_hex(32))"`

2. **Disable Debug Mode**
   ```yaml
   server:
     debug: false
   ```

3. **Use HTTPS** (via reverse proxy)

4. **Set up Fail2Ban** (protect against brute force)
   ```bash
   sudo apt install fail2ban
   ```

5. **Regular Backups**
   ```bash
   # Backup database and uploads
   rsync -avz /opt/cloud-storage/instance/ /backup/cloud-storage/
   rsync -avz /opt/cloud-storage/uploads/ /backup/cloud-storage-uploads/
   ```

6. **Monitor Logs**
   ```bash
   sudo journalctl -u cloud-storage-server -f
   ```

---

## Testing Your Deployment

### 1. Local Network Test

```bash
# From VM, test server is running
curl http://localhost:5000/api/v1/auth/verify

# From another machine on your network
curl http://192.168.1.100:5000/api/v1/auth/verify
```

### 2. External Access Test

```bash
# From outside your network (use phone with wifi off, or online curl service)
curl http://your-public-ip:5000/api/v1/auth/verify
```

### 3. Client Test

1. Run the executable
2. Login with test credentials
3. Upload a file
4. Download a file
5. Check server logs for any errors

---

## Troubleshooting

### Server Not Accessible Externally

1. Check router port forwarding is configured
2. Verify firewall allows the port: `sudo ufw status`
3. Check your public IP: `curl ifconfig.me`
4. Test with: `curl http://your-public-ip:5000/api/v1/auth/verify`

### Client Can't Connect

1. Verify `server_url` in `config.yaml` is correct
2. Check server is running: `sudo systemctl status cloud-storage-server`
3. Check server logs: `sudo journalctl -u cloud-storage-server -n 50`
4. Verify firewall isn't blocking on client side

### Docker Container Issues

```bash
# View logs
docker-compose logs -f

# Restart containers
docker-compose restart

# Rebuild if code changed
docker-compose down
docker-compose up -d --build
```

### Permission Issues

```bash
# Fix file permissions
sudo chown -R www-data:www-data /opt/cloud-storage/uploads
sudo chown -R www-data:www-data /opt/cloud-storage/instance
```

---

## Maintenance

### Updates

```bash
# Pull latest code
cd /opt/cloud-storage
git pull

# Restart service
sudo systemctl restart cloud-storage-server

# Or with Docker
docker-compose down
docker-compose up -d --build
```

### Monitoring Resource Usage

```bash
# Check disk space
df -h

# Check memory
free -h

# Check running processes
htop
```

### Database Backup

```bash
# Create backup script
cat > /opt/cloud-storage/backup.sh << 'EOF'
#!/bin/bash
BACKUP_DIR="/backup/cloud-storage"
DATE=$(date +%Y%m%d_%H%M%S)

mkdir -p $BACKUP_DIR
sqlite3 /opt/cloud-storage/instance/csc455_homelab.db ".backup $BACKUP_DIR/db_$DATE.db"
tar -czf $BACKUP_DIR/uploads_$DATE.tar.gz /opt/cloud-storage/uploads

# Keep only last 7 days
find $BACKUP_DIR -type f -mtime +7 -delete
EOF

chmod +x /opt/cloud-storage/backup.sh

# Add to crontab (daily at 2 AM)
(crontab -l 2>/dev/null; echo "0 2 * * * /opt/cloud-storage/backup.sh") | crontab -
```

---

## Quick Start Commands

### Server (Proxmox VM)

```bash
# Start
sudo systemctl start cloud-storage-server

# Stop
sudo systemctl stop cloud-storage-server

# Restart
sudo systemctl restart cloud-storage-server

# Status
sudo systemctl status cloud-storage-server

# Logs
sudo journalctl -u cloud-storage-server -f
```

### Client (Windows)

Just double-click `CloudStorageClient.exe`!

---

## Architecture Overview

```
Internet
    ↓
Your Router (Port Forward 5000 → 443)
    ↓
Proxmox Host
    ↓
Ubuntu VM/LXC (192.168.1.100)
    ├── Nginx (Reverse Proxy, SSL) :443
    │   ↓
    └── Flask Server :5000
        ├── SQLite Database
        └── File Storage (/uploads)
```

Client connects to: `https://yourdomain.com` → Nginx → Flask

---

## Next Steps

1. ✅ Set up Proxmox VM
2. ✅ Install Docker or systemd service
3. ✅ Configure networking (port forwarding)
4. ✅ Build client executable
5. ✅ Test locally then externally
6. 🔒 Set up SSL with Let's Encrypt
7. 📱 Share executable with users
8. 📊 Monitor and maintain

Need help with any step? Let me know!
