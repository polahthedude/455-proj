# Quick Reference - Cloud Storage Deployment

## For Server Deployment (Proxmox)

### Docker (Easiest)
```bash
# On your Proxmox VM
cd /opt/cloud-storage
docker-compose up -d
docker-compose logs -f
```

### Systemd Service
```bash
# Start/stop/restart
sudo systemctl start cloud-storage-server
sudo systemctl stop cloud-storage-server
sudo systemctl restart cloud-storage-server

# View logs
sudo journalctl -u cloud-storage-server -f
```

### Networking
```bash
# Open firewall
sudo ufw allow 5000/tcp
sudo ufw enable

# Test locally
curl http://localhost:5000/api/v1/auth/verify

# Test from network
curl http://192.168.1.100:5000/api/v1/auth/verify
```

---

## For Building Client Executables

### Build Client
```bash
.\deployment\build_client.bat
```
→ Creates `dist\CloudStorageClient.exe`

### Package for Users
```bash
.\deployment\package_client.bat
```
→ Creates `dist\CloudStorageClient-Package.zip`

### Build Server (Windows)
```bash
.\deployment\build_server.bat
```
→ Creates `dist\CloudStorageServer.exe`

---

## Configuration Files

### Server Config (`config.yaml`)
```yaml
server:
  host: "0.0.0.0"           # Listen on all interfaces
  port: 5000
  debug: false              # MUST be false in production
  secret_key: "CHANGE-THIS" # Generate with secrets.token_hex(32)
```

### Client Config (`config.yaml`)
```yaml
client:
  server_url: "https://yourdomain.com"  # Your server URL
```

---

## Port Forwarding

**Router Setup:**
- External Port: 5000 (or 443 for HTTPS)
- Internal IP: 192.168.1.100
- Internal Port: 5000

---

## SSL with Nginx

```bash
# Install
sudo apt install nginx certbot python3-certbot-nginx

# Configure (edit domain in file)
sudo cp deployment/nginx-config /etc/nginx/sites-available/cloud-storage
sudo ln -s /etc/nginx/sites-available/cloud-storage /etc/nginx/sites-enabled/

# Get certificate
sudo certbot --nginx -d yourdomain.com
```

---

## Useful Commands

### Docker
```bash
docker-compose up -d        # Start
docker-compose down         # Stop
docker-compose restart      # Restart
docker-compose logs -f      # View logs
docker-compose ps           # Status
```

### Systemd
```bash
sudo systemctl status cloud-storage-server   # Status
sudo systemctl restart cloud-storage-server  # Restart
sudo journalctl -u cloud-storage-server -n 50 # Last 50 log lines
```

### Testing
```bash
# Health check
curl http://localhost:5000/api/v1/auth/verify

# From another machine
curl http://your-ip:5000/api/v1/auth/verify

# With HTTPS
curl https://yourdomain.com/api/v1/auth/verify
```

### Monitoring
```bash
df -h                    # Disk space
free -h                  # Memory
htop                     # CPU/Memory usage
sudo ufw status          # Firewall status
```

---

## Quick Troubleshooting

### Server won't start
```bash
# Check logs
sudo journalctl -u cloud-storage-server -n 50
# or
docker-compose logs

# Check if port is in use
sudo netstat -tlnp | grep 5000
```

### Can't connect externally
```bash
# Check firewall
sudo ufw status

# Check if listening on all interfaces
sudo netstat -tlnp | grep 5000
# Should show 0.0.0.0:5000 not 127.0.0.1:5000

# Test from external
curl http://your-public-ip:5000/api/v1/auth/verify
```

### Client can't connect
1. Check server URL in `config.yaml`
2. Ping/curl the server URL
3. Check firewall on both ends
4. Verify server is running

---

## Security Checklist

- [ ] Changed default secret_key
- [ ] Set debug: false
- [ ] Using HTTPS (with SSL certificate)
- [ ] Firewall configured
- [ ] Backups configured
- [ ] Monitoring set up

---

## Emergency Commands

```bash
# Restart everything
sudo systemctl restart cloud-storage-server
# or
docker-compose restart

# View recent errors
sudo journalctl -u cloud-storage-server -p err -n 50

# Check system resources
df -h && free -h

# Force stop and clean restart (Docker)
docker-compose down
docker-compose up -d --force-recreate
```

---

## File Locations

- Server code: `/opt/cloud-storage/`
- Database: `/opt/cloud-storage/instance/csc455_homelab.db`
- Uploaded files: `/opt/cloud-storage/uploads/`
- Logs: `sudo journalctl -u cloud-storage-server`
- Config: `/opt/cloud-storage/config.yaml`

---

## Support

📖 Full guide: `DEPLOYMENT.md`
✅ Checklist: `DEPLOYMENT_CHECKLIST.md`
🔧 Troubleshooting: `TROUBLESHOOTING.md`

---

**Quick tip**: Bookmark this file for fast reference!
