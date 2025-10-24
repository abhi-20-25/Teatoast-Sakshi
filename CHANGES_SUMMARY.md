# 📝 Changes Summary - EC2 Deployment Configuration

## Overview
All necessary code changes have been implemented to deploy Sakshi.AI on your EC2 server (13.200.138.25) with PostgreSQL running on Ubuntu instead of in a Docker container.

---

## ✅ Files Modified

### 1. `templates/dashboard.html`
**Line 172 - Socket.IO Connection**

**Before:**
```javascript
const socket = io();
```

**After:**
```javascript
const socket = io(`http://${window.location.hostname}:5001`);
```

**Purpose:** Allows Socket.IO to connect properly when accessing from remote IP address (13.200.138.25) instead of just working on localhost.

---

### 2. `docker-compose.yml`
**Multiple changes for host PostgreSQL integration**

#### Change 1: Removed PostgreSQL Container
**Removed lines 2-20:**
- Entire `postgres` service definition removed
- Application will now use PostgreSQL installed on Ubuntu host

#### Change 2: Updated DATABASE_URL (All Services)
**Updated in ALL processor services:**
```yaml
# Before:
- DATABASE_URL=postgresql+psycopg2://postgres:Tneural01@localhost:5433/sakshi

# After:
- DATABASE_URL=postgresql+psycopg2://postgres:Tneural01@127.0.0.1:5432/sakshi
```

**Changes:**
- `localhost` → `127.0.0.1` (explicit IP for host networking)
- Port `5433` → `5432` (standard PostgreSQL port)

**Applied to services:**
- ✅ main-app
- ✅ detection-processor
- ✅ people-counter-processor
- ✅ heatmap-processor
- ✅ kitchen-compliance-processor
- ✅ queue-monitor-processor
- ✅ security-monitor-processor
- ✅ shutter-monitor-processor

#### Change 3: Removed PostgreSQL Dependencies
**Removed from all services:**
```yaml
depends_on:
  - postgres  # ← Removed this line
  - main-app
```

#### Change 4: Removed PostgreSQL Volume
**Removed lines 235-236:**
```yaml
volumes:
  postgres_data:  # ← Removed
```

---

### 3. `main_app.py`
**Line 31 - Database URL Configuration**

**Before:**
```python
DATABASE_URL = os.environ.get('DATABASE_URL', "postgresql+psycopg2://postgres:Tneural01@localhost:5432/sakshi")
```

**After:**
```python
DATABASE_URL = os.environ.get('DATABASE_URL', "postgresql+psycopg2://postgres:Tneural01@127.0.0.1:5432/sakshi")
```

**Purpose:** Ensures standalone mode (without Docker) also uses explicit 127.0.0.1 for consistency.

---

## 📁 New Files Created

### 1. `DEPLOYMENT_EC2.md`
Complete deployment guide covering:
- System dependencies installation
- PostgreSQL setup and configuration
- Docker installation
- Firewall configuration
- Application deployment
- Management commands
- Troubleshooting guide
- Security best practices

### 2. `setup_postgres.sh`
Automated PostgreSQL setup script that:
- Installs PostgreSQL
- Creates `sakshi` database
- Configures database user
- Sets up TCP connections on 127.0.0.1
- Tests the connection
- **Usage:** `./setup_postgres.sh`

### 3. `deploy.sh`
Interactive deployment script with options:
1. Deploy (build and start)
2. Restart services
3. Stop services
4. View logs
5. Check status
6. Rebuild
7. Clean up
8. Exit
- **Usage:** `./deploy.sh`

### 4. `QUICKSTART.md`
Quick reference guide for:
- Installation steps
- Configuration
- Common commands
- Troubleshooting

### 5. `CHANGES_SUMMARY.md` (this file)
Documentation of all changes made

---

## 🔧 Configuration Details

### Database Connection
```
Host: 127.0.0.1
Port: 5432
Database: sakshi
Username: postgres
Password: Tneural01
```

### Connection String
```
postgresql+psycopg2://postgres:Tneural01@127.0.0.1:5432/sakshi
```

### Network Architecture
- All Docker containers use `network_mode: "host"`
- Containers can access host PostgreSQL via 127.0.0.1:5432
- Web dashboard accessible on port 5001

---

## 🚀 Deployment Steps

### Quick Deployment
```bash
# 1. Setup PostgreSQL
./setup_postgres.sh

# 2. Deploy application
./deploy.sh
# Select option 1 (Deploy)

# 3. Access dashboard
# http://13.200.138.25:5001/dashboard
```

### Manual Deployment
```bash
# 1. Install PostgreSQL
sudo apt install postgresql postgresql-contrib -y
sudo -u postgres psql -c "CREATE DATABASE sakshi;"

# 2. Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# 3. Install Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# 4. Configure firewall
sudo ufw allow 22/tcp
sudo ufw allow 5001/tcp

# 5. Deploy
docker-compose build
docker-compose up -d
```

---

## 🔍 Verification Steps

### 1. Check PostgreSQL
```bash
sudo systemctl status postgresql
PGPASSWORD='Tneural01' psql -h 127.0.0.1 -U postgres -d sakshi -c "SELECT 1;"
```

### 2. Check Docker Containers
```bash
docker-compose ps
# All services should show "Up" status
```

### 3. Check Application Health
```bash
curl http://localhost:5001/health
# Expected: {"status":"healthy","timestamp":"..."}
```

### 4. Check Dashboard Access
```
Browser: http://13.200.138.25:5001/dashboard
```

---

## 🐛 Common Issues & Solutions

### Issue: Live feed not showing
**Solution:**
1. Check browser console for Socket.IO errors
2. Verify containers are running: `docker-compose ps`
3. Clear browser cache and hard reload (Ctrl+F5)

### Issue: Database connection refused
**Solution:**
```bash
# Check PostgreSQL is running
sudo systemctl status postgresql

# Check if listening on 127.0.0.1
sudo netstat -tulpn | grep 5432

# Test connection
PGPASSWORD='Tneural01' psql -h 127.0.0.1 -U postgres -d sakshi
```

### Issue: Port 5001 not accessible from outside
**Solution:**
```bash
# Check firewall
sudo ufw status

# Check AWS Security Group
# EC2 Console → Security Groups → Add port 5001

# Check if port is listening
sudo netstat -tulpn | grep 5001
```

---

## 📊 Architecture Diagram

```
┌─────────────────────────────────────────┐
│         EC2 Server (13.200.138.25)      │
│                                          │
│  ┌────────────────────────────────────┐ │
│  │  Ubuntu Host                       │ │
│  │                                    │ │
│  │  ┌──────────────────────────────┐ │ │
│  │  │  PostgreSQL (port 5432)      │ │ │
│  │  │  - Database: sakshi          │ │ │
│  │  │  - User: postgres            │ │ │
│  │  └──────────────────────────────┘ │ │
│  │            ↑                       │ │
│  │            │ 127.0.0.1:5432       │ │
│  │            │                       │ │
│  │  ┌─────────┴──────────────────────┤ │
│  │  │  Docker Containers             │ │
│  │  │  (network_mode: host)          │ │
│  │  │                                │ │ │
│  │  │  - main-app (port 5001)       │ │ │
│  │  │  - detection-processor         │ │ │
│  │  │  - people-counter-processor    │ │ │
│  │  │  - heatmap-processor           │ │ │
│  │  │  - kitchen-compliance         │ │ │
│  │  │  - queue-monitor               │ │ │
│  │  │  - security-monitor            │ │ │
│  │  │  - shutter-monitor             │ │ │
│  │  └────────────────────────────────┘ │ │
│  └────────────────────────────────────┘ │
│                 ↓                        │
│          Port 5001 (HTTP)                │
└─────────────────────────────────────────┘
                  ↓
          Internet (0.0.0.0/0)
                  ↓
        Users accessing dashboard
   http://13.200.138.25:5001/dashboard
```

---

## 📋 Checklist

Before deployment:
- [ ] Code uploaded to EC2 server
- [ ] PostgreSQL installed on Ubuntu
- [ ] Database `sakshi` created
- [ ] Docker installed
- [ ] Docker Compose installed
- [ ] Firewall configured (UFW)
- [ ] AWS Security Group configured
- [ ] Camera URLs configured in `config/rtsp_links.txt`
- [ ] Model files (.pt) in `models/` directory

After deployment:
- [ ] All containers running (`docker-compose ps`)
- [ ] PostgreSQL accessible (`psql -h 127.0.0.1 -U postgres -d sakshi`)
- [ ] Health endpoint working (`curl http://localhost:5001/health`)
- [ ] Dashboard accessible from browser
- [ ] Live feeds showing in dashboard
- [ ] Socket.IO connected (check browser console)

---

## 🎯 Next Steps

1. **Configure Cameras:**
   - Edit `config/rtsp_links.txt`
   - Add your camera RTSP URLs

2. **Add Model Files:**
   - Upload `.pt` model files to `models/` directory
   - Required models listed in `main_app.py` line 42-49

3. **Test Application:**
   - Access dashboard
   - Verify live feeds
   - Check detection history

4. **Set Up Monitoring:**
   - Check logs regularly: `docker-compose logs -f`
   - Monitor disk space: `df -h`
   - Monitor database size

5. **Backup Configuration:**
   ```bash
   # Backup database
   pg_dump -h 127.0.0.1 -U postgres sakshi > backup_$(date +%Y%m%d).sql
   
   # Backup config
   tar -czf config_backup.tar.gz config/
   ```

---

## 📞 Support Resources

- **Deployment Guide:** `DEPLOYMENT_EC2.md`
- **Quick Start:** `QUICKSTART.md`
- **Setup Script:** `./setup_postgres.sh`
- **Deploy Script:** `./deploy.sh`

---

**✅ All changes have been successfully implemented!**

Your application is now ready to deploy on EC2 server 13.200.138.25.

For deployment, follow the steps in `QUICKSTART.md` or run `./deploy.sh`.

