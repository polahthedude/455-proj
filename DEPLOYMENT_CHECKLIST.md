# Deployment Checklist

Use this checklist to ensure smooth deployment of your Cloud Storage system.

## Pre-Deployment

### Server Preparation
- [ ] Proxmox VM/Container created (Ubuntu 22.04 LTS)
- [ ] Static IP assigned (e.g., 192.168.1.100)
- [ ] SSH access configured
- [ ] Basic packages updated: `sudo apt update && sudo apt upgrade -y`

### Network Planning
- [ ] Decided on deployment method (Docker or Systemd)
- [ ] Internal IP address documented: `__________________`
- [ ] External access needed? Yes / No
- [ ] Domain name registered (if using): `__________________`
- [ ] Router access available for port forwarding

### Security Planning
- [ ] Generated secure secret key
  - Command: `python -c "import secrets; print(secrets.token_hex(32))"`
  - Key saved securely: `__________________`
- [ ] SSL certificate plan (Let's Encrypt, Cloudflare, etc.)
- [ ] Backup strategy defined

---

## Server Deployment

### Option A: Docker Deployment (Recommended)

- [ ] Docker installed on VM
  ```bash
  curl -fsSL https://get.docker.com -o get-docker.sh
  sudo sh get-docker.sh
  sudo apt install docker-compose -y
  ```
- [ ] Project files transferred to VM: `/opt/cloud-storage` or `/home/user/cloud-storage`
- [ ] Configuration updated in `config.yaml`:
  - [ ] `server.host` = `"0.0.0.0"`
  - [ ] `server.debug` = `false`
  - [ ] `server.secret_key` = your generated key
- [ ] `.env` file created from template
- [ ] Docker containers started: `docker-compose up -d`
- [ ] Health check passed: `docker-compose logs`
- [ ] Server accessible locally: `curl http://localhost:5000/api/v1/auth/verify`

### Option B: Systemd Service

- [ ] Python 3.11+ installed
- [ ] Virtual environment created: `python3 -m venv venv`
- [ ] Dependencies installed: `pip install -r requirements.txt`
- [ ] Configuration updated (same as Docker option)
- [ ] Service file copied: `sudo cp deployment/cloud-storage-server.service /etc/systemd/system/`
- [ ] Service enabled: `sudo systemctl enable cloud-storage-server`
- [ ] Service started: `sudo systemctl start cloud-storage-server`
- [ ] Service status verified: `sudo systemctl status cloud-storage-server`
- [ ] Logs checked: `sudo journalctl -u cloud-storage-server -n 50`

### Network Configuration

- [ ] Firewall configured:
  ```bash
  sudo ufw allow 5000/tcp
  sudo ufw enable
  sudo ufw status
  ```
- [ ] Server accessible from other machine on LAN:
  - Test: `curl http://192.168.1.100:5000/api/v1/auth/verify`
  - Result: ☐ Success ☐ Failed

### External Access (if needed)

- [ ] Router port forwarding configured:
  - External port: `__________` → Internal: `192.168.1.100:5000`
- [ ] Public IP documented: `__________________`
- [ ] Tested from external network (mobile data): ☐ Success ☐ Failed
- [ ] Dynamic DNS configured (if no static IP): Service: `__________________`

### Reverse Proxy with SSL (Recommended for Production)

- [ ] Nginx installed: `sudo apt install nginx -y`
- [ ] Config copied: `sudo cp deployment/nginx-config /etc/nginx/sites-available/cloud-storage`
- [ ] Config customized (domain name updated)
- [ ] Config enabled: `sudo ln -s /etc/nginx/sites-available/cloud-storage /etc/nginx/sites-enabled/`
- [ ] Nginx tested: `sudo nginx -t`
- [ ] Nginx restarted: `sudo systemctl restart nginx`
- [ ] Certbot installed: `sudo apt install certbot python3-certbot-nginx -y`
- [ ] SSL certificate obtained: `sudo certbot --nginx -d yourdomain.com`
- [ ] Auto-renewal tested: `sudo certbot renew --dry-run`
- [ ] HTTPS access verified: `https://yourdomain.com`

---

## Client Executable Creation

### Build Environment Setup

- [ ] PyInstaller installed: `pip install pyinstaller`
- [ ] All dependencies installed: `pip install -r requirements.txt`
- [ ] Build scripts executable

### Building Client Executable

- [ ] Client executable built: `.\deployment\build_client.bat`
- [ ] Build successful: `dist\CloudStorageClient.exe` exists
- [ ] Executable size reasonable (< 50MB typically)

### Client Configuration

- [ ] `config.yaml` updated with your server URL:
  ```yaml
  client:
    server_url: "https://yourdomain.com"  # YOUR URL HERE
  ```
- [ ] Or: Setup wizard configured to prompt user
- [ ] Config file included with executable for distribution

### Testing Client Executable

- [ ] Tested on development machine: ☐ Success ☐ Failed
- [ ] Tested on clean machine (no Python installed): ☐ Success ☐ Failed
- [ ] Login works
- [ ] File upload works
- [ ] File download works
- [ ] File listing works

---

## Distribution

### Client Distribution Package

- [ ] Created distribution folder containing:
  - [ ] `CloudStorageClient.exe`
  - [ ] `config.yaml` (with your server URL)
  - [ ] `README.txt` with basic instructions
- [ ] Compressed as ZIP
- [ ] Upload location prepared: `__________________`

### Documentation for Users

- [ ] Quick start guide created
- [ ] Server URL provided to users
- [ ] Support contact info included

---

## Post-Deployment

### Initial Testing

- [ ] Create test user account
- [ ] Upload test file (small)
- [ ] Upload test file (large, ~90MB)
- [ ] Download file
- [ ] Delete file
- [ ] Test from multiple clients simultaneously
- [ ] Verify file encryption (check uploads folder - files should be encrypted)

### Monitoring Setup

- [ ] Log monitoring configured
  - Docker: `docker-compose logs -f`
  - Systemd: `sudo journalctl -u cloud-storage-server -f`
- [ ] Disk space monitoring
- [ ] Resource usage monitoring (htop, Proxmox dashboard)

### Backup Configuration

- [ ] Backup script created
- [ ] Cron job configured
- [ ] Test backup performed
- [ ] Backup restoration tested
- [ ] Backup location: `__________________`

### Security Hardening

- [ ] Default secret key changed ✓
- [ ] Debug mode disabled ✓
- [ ] Fail2ban configured (optional):
  ```bash
  sudo apt install fail2ban
  # Configure for your setup
  ```
- [ ] Rate limiting verified in config
- [ ] User password requirements verified
- [ ] SSL/HTTPS in use (if external access)

---

## Troubleshooting Tests

- [ ] What happens if server restarts?
  - Docker: `docker-compose restart` - should auto-recover
  - Systemd: `sudo systemctl restart cloud-storage-server` - should auto-recover
- [ ] What happens if VM restarts?
  - Services start automatically: ☐ Yes ☐ No (fix if no)
- [ ] Can access server from:
  - [ ] Same machine (localhost)
  - [ ] Local network (192.168.x.x)
  - [ ] External network (if configured)
- [ ] Logs accessible and readable
- [ ] Error handling works (test wrong password, large file, etc.)

---

## Maintenance Schedule

### Daily
- [ ] Check logs for errors
- [ ] Verify service is running

### Weekly
- [ ] Review disk space usage
- [ ] Check backup success
- [ ] Review user activity (if monitoring)

### Monthly
- [ ] Update system packages: `sudo apt update && sudo apt upgrade`
- [ ] Review and rotate logs
- [ ] Test backup restoration
- [ ] Review security logs

### Quarterly
- [ ] Update application (if updates available)
- [ ] Review and update documentation
- [ ] Security audit

---

## Emergency Contacts & Info

### Important Paths
- Server installation: `__________________`
- Database location: `__________________`
- Upload storage: `__________________`
- Backup location: `__________________`
- Log location: `__________________`

### Access Information
- VM IP: `__________________`
- VM SSH: `ssh user@__________________`
- Public URL: `__________________`
- Admin account: `__________________`

### Quick Commands
```bash
# Check service status
sudo systemctl status cloud-storage-server
# or
docker-compose ps

# View logs
sudo journalctl -u cloud-storage-server -n 100
# or
docker-compose logs --tail=100

# Restart service
sudo systemctl restart cloud-storage-server
# or
docker-compose restart

# Check disk space
df -h

# Check memory
free -h
```

---

## Success Criteria

Deployment is successful when:
- [x] Server is running and accessible
- [x] Client executable works on external machine
- [x] Users can register, login, upload, and download files
- [x] Data persists across server restarts
- [x] Backups are working
- [x] Logs are accessible
- [x] No critical errors in logs

---

## Notes

Space for your own notes during deployment:

```








```

---

**Deployment Date:** __________________
**Deployed By:** __________________
**Version:** __________________
**Status:** ☐ In Progress ☐ Complete ☐ Issues Found
