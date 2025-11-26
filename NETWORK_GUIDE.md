# Network Architecture

## Deployment Topology

```
Internet (Cloud Access)
         |
         | Port forwarding / DDNS
         |
    Your Router
    (Public IP)
         |
         | Forward port 443 (HTTPS) or 5000 (HTTP)
         |
    Home Network
    (192.168.1.x)
         |
    ┌────┴─────┐
    |          |
Proxmox    Other
Host       Devices
    |
    └── Ubuntu VM/Container
        IP: 192.168.1.100
        |
        ├── Nginx :443 (HTTPS) ─┐
        │   - SSL Termination    │
        │   - Reverse Proxy      │
        │                        ↓
        └── Flask Server :5000 ←─┘
            - API Endpoints
            - File Storage
            - SQLite Database
```

## Access Paths

### Local Network Access (Development)
```
Client PC → 192.168.1.100:5000 → Flask Server
```

### Local Network Access (Production with SSL)
```
Client PC → 192.168.1.100:443 → Nginx → Flask Server :5000
```

### Internet Access (Production)
```
Client PC
    ↓ Internet
Router (your-public-ip:443 or yourdomain.com:443)
    ↓ Port Forward to 192.168.1.100:443
Nginx :443
    ↓ Reverse Proxy
Flask Server :5000
```

## Port Configuration

### Required Open Ports

**On VM Firewall:**
- Port 5000/tcp - Flask application (internal)
- Port 443/tcp - HTTPS (if using Nginx with SSL)
- Port 80/tcp - HTTP redirect (if using Nginx with SSL)
- Port 22/tcp - SSH (for management)

**On Router (Port Forwarding):**
- External 443 → Internal 192.168.1.100:443 (for HTTPS)
- OR External 5000 → Internal 192.168.1.100:5000 (for HTTP)

### Firewall Commands

**Ubuntu VM:**
```bash
# Allow Flask server
sudo ufw allow 5000/tcp

# Allow HTTPS/HTTP (if using Nginx)
sudo ufw allow 443/tcp
sudo ufw allow 80/tcp

# Allow SSH
sudo ufw allow 22/tcp

# Enable firewall
sudo ufw enable

# Check status
sudo ufw status numbered
```

**Router:**
- Configure via web interface (typically http://192.168.1.1)
- Different for each router brand
- Look for "Port Forwarding" or "Virtual Server" section

## Domain Name Setup

### Option 1: Static Public IP + Domain
1. Register domain (e.g., Namecheap, Cloudflare)
2. Point A record to your public IP
3. Configure SSL with Let's Encrypt

### Option 2: Dynamic DNS (Home Internet)
Popular DDNS providers:
- **DuckDNS** (Free, simple)
  - Create account at duckdns.org
  - Choose subdomain: mycloud.duckdns.org
  - Install update client on VM or router

- **No-IP** (Free tier available)
  - Free hostname: mycloud.ddns.net
  - Update client available

- **Cloudflare Tunnel** (Free, no port forwarding needed!)
  - Most secure option
  - No need to open ports on router
  - Free SSL included

## Recommended Setups

### Setup 1: Simple Local Network (No External Access)
```
Client → 192.168.1.100:5000 → Flask
```
**Pros:** Simple, no router config, secure
**Cons:** Only works on local network

### Setup 2: Direct HTTP Access (Development/Testing)
```
Client → your-public-ip:5000 → Router → Flask
```
**Pros:** Simple, fast to set up
**Cons:** No encryption, not secure for production

### Setup 3: HTTPS with Let's Encrypt (Recommended)
```
Client → yourdomain.com:443 → Router → Nginx (SSL) → Flask
```
**Pros:** Secure, professional, encrypted
**Cons:** Requires domain name, more setup

### Setup 4: Cloudflare Tunnel (Most Secure)
```
Client → yourdomain.com → Cloudflare → Tunnel → Flask
```
**Pros:** Most secure, no port forwarding, free SSL, DDoS protection
**Cons:** Requires Cloudflare account, slight latency

## Security Layers

```
Layer 1: Network
├── Router firewall (NAT)
├── Port forwarding (only necessary ports)
└── VM firewall (ufw)

Layer 2: Transport
├── HTTPS/TLS encryption (Nginx)
└── Certificate validation (Let's Encrypt)

Layer 3: Application
├── JWT authentication
├── Rate limiting
├── Password hashing (bcrypt)
└── Input validation

Layer 4: Data
├── End-to-end encryption (client-side)
├── AES-256-GCM
└── RSA-2048 key exchange
```

## IP Address Planning

### Suggested Configuration

**Proxmox Host:**
- IP: 192.168.1.10/24
- Gateway: 192.168.1.1

**Cloud Storage VM:**
- IP: 192.168.1.100/24
- Gateway: 192.168.1.1
- DNS: 8.8.8.8, 8.8.4.4

**Other Services (if any):**
- IP: 192.168.1.101+
- Keep range for expansion

## DNS Configuration

### Internal DNS (Optional but Recommended)

Edit `/etc/hosts` on your machines:
```
192.168.1.100    cloud.local
192.168.1.100    cloud.homelab
```

Now you can use: `http://cloud.local:5000`

### External DNS (For Internet Access)

**A Record Example:**
```
Type: A
Name: cloud (or @)
Value: your-public-ip
TTL: 300
```

Result: `cloud.yourdomain.com` → Your server

## Testing Network Configuration

### Test 1: Local VM
```bash
# On the VM
curl http://localhost:5000/api/v1/auth/verify
# Should return: {"status": "online"}
```

### Test 2: Local Network
```bash
# From another computer on same network
curl http://192.168.1.100:5000/api/v1/auth/verify
```

### Test 3: External Network
```bash
# From phone (cellular data, not WiFi) or external service
curl http://your-public-ip:5000/api/v1/auth/verify
# or
curl https://yourdomain.com/api/v1/auth/verify
```

### Test 4: DNS Resolution
```bash
# Check if domain resolves
nslookup yourdomain.com
ping yourdomain.com
```

## Bandwidth Considerations

### Upload Speed Requirements

For comfortable file uploads:
- Minimum: 5 Mbps upload
- Recommended: 10+ Mbps upload
- Ideal: 25+ Mbps upload

**Calculate upload time:**
- 100MB file on 10 Mbps = ~80 seconds
- 100MB file on 25 Mbps = ~32 seconds

### Concurrent Users

Approximate capacity:
- Light use (documents): 10-20 users
- Medium use (photos): 5-10 users  
- Heavy use (videos): 2-5 users

## Common Network Issues

### Can't access from local network
- Check VM firewall: `sudo ufw status`
- Verify Flask is listening on 0.0.0.0, not 127.0.0.1
- Check VM IP with: `ip addr show`

### Can't access from internet
- Verify public IP: `curl ifconfig.me`
- Check router port forwarding is enabled
- Test from external network (mobile data)
- Verify ISP doesn't block incoming ports

### Slow connections
- Check bandwidth: speedtest.net
- Monitor VM resources: `htop`
- Check for network congestion
- Consider QoS on router

### SSL certificate issues
- Verify domain points to your IP
- Check certbot logs: `sudo journalctl -u certbot`
- Ensure ports 80 and 443 are open
- Test certificate: `openssl s_client -connect yourdomain.com:443`

---

## Quick Network Checklist

- [ ] VM has static IP assigned
- [ ] VM can access internet
- [ ] Firewall rules configured
- [ ] Port forwarding configured (if external access)
- [ ] Domain name configured (if applicable)
- [ ] SSL certificate obtained (if HTTPS)
- [ ] Tested from local network
- [ ] Tested from external network (if applicable)
- [ ] DNS resolves correctly
- [ ] No ISP port blocking

---

For more details, see `DEPLOYMENT.md`
