# 🚀 Sakshi.AI Deployment Guide for EC2 Server (13.200.138.25)

## 📋 Overview
This guide will help you deploy Sakshi.AI on your EC2 Ubuntu server using:
- **PostgreSQL** installed directly on Ubuntu (not in Docker)
- **Docker containers** for all application services
- **Host networking** for easy communication

---

## ✅ Prerequisites

- Ubuntu 20.04 or 22.04 on EC2
- Root or sudo access
- At least 8GB RAM, 50GB storage
- NVIDIA GPU (optional, for GPU-accelerated inference)

---

## 📦 Part 1: Install System Dependencies

### 1.1 Update System
```bash
sudo apt update && sudo apt upgrade -y
```

### 1.2 Install Docker
```bash
# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Add your user to docker group
sudo usermod -aG docker $USER

# Log out and log back in for group changes to take effect
exit
# SSH back into the server
```

### 1.3 Install Docker Compose
```bash
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Verify installation
docker --version
docker-compose --version
```

### 1.4 Install NVIDIA Docker (If you have GPU)
```bash
# Check if you have NVIDIA GPU
nvidia-smi

# If yes, install nvidia-docker
distribution=$(. /etc/os-release;echo $ID$VERSION_ID)
curl -s -L https://nvidia.github.io/nvidia-docker/gpgkey | sudo apt-key add -
curl -s -L https://nvidia.github.io/nvidia-docker/$distribution/nvidia-docker.list | sudo tee /etc/apt/sources.list.d/nvidia-docker.list

sudo apt-get update
sudo apt-get install -y nvidia-docker2
sudo systemctl restart docker

# Test GPU access from Docker
docker run --rm --gpus all nvidia/cuda:11.8.0-base-ubuntu20.04 nvidia-smi
```

---

## 🗄️ Part 2: Install and Configure PostgreSQL

### 2.1 Install PostgreSQL
```bash
# Install PostgreSQL
sudo apt install postgresql postgresql-contrib -y

# Start and enable PostgreSQL
sudo systemctl start postgresql
sudo systemctl enable postgresql

# Check status
sudo systemctl status postgresql
```

### 2.2 Create Database and User
```bash
# Switch to postgres user and create database
sudo -u postgres psql <<EOF
CREATE DATABASE sakshi;
CREATE USER postgres WITH PASSWORD 'Tneural01';
ALTER USER postgres WITH SUPERUSER;
GRANT ALL PRIVILEGES ON DATABASE sakshi TO postgres;
\q
EOF
```

### 2.3 Configure PostgreSQL for TCP Connections
```bash
# Find PostgreSQL version
PG_VERSION=$(ls /etc/postgresql/)

# Edit postgresql.conf to listen on localhost
sudo sed -i "s/#listen_addresses = 'localhost'/listen_addresses = 'localhost,127.0.0.1'/" /etc/postgresql/$PG_VERSION/main/postgresql.conf

# Add authentication rules
echo "host    sakshi          postgres        127.0.0.1/32            md5" | sudo tee -a /etc/postgresql/$PG_VERSION/main/pg_hba.conf
echo "host    all             postgres        127.0.0.1/32            md5" | sudo tee -a /etc/postgresql/$PG_VERSION/main/pg_hba.conf

# Restart PostgreSQL
sudo systemctl restart postgresql
```

### 2.4 Test PostgreSQL Connection
```bash
# Test connection (password: Tneural01)
psql -h 127.0.0.1 -U postgres -d sakshi

# If successful, you'll see the psql prompt. Type \q to exit
```

---

## 🔥 Part 3: Configure Firewall and Security Groups

### 3.1 Configure Ubuntu Firewall (UFW)
```bash
# Enable firewall
sudo ufw enable

# Allow SSH (IMPORTANT!)
sudo ufw allow 22/tcp

# Allow application port
sudo ufw allow 5001/tcp

# Check firewall status
sudo ufw status
```

### 3.2 Configure AWS Security Group
Go to AWS Console → EC2 → Security Groups:

**Add these Inbound Rules:**
| Type       | Protocol | Port | Source    | Description          |
|------------|----------|------|-----------|----------------------|
| SSH        | TCP      | 22   | Your IP   | SSH Access           |
| Custom TCP | TCP      | 5001 | 0.0.0.0/0 | Sakshi.AI Web Access |

---

## 📁 Part 4: Deploy the Application

### 4.1 Upload Code to Server
```bash
# On your local machine, upload the code to EC2
scp -r /path/to/Sakshi-21-OCT ubuntu@13.200.138.25:~/

# Or use git clone if you have a repository
# ssh ubuntu@13.200.138.25
# git clone <your-repo-url>
```

### 4.2 Navigate to Project Directory
```bash
cd ~/Sakshi-21-OCT
```

### 4.3 Verify Code Changes
All necessary changes have been made to:
- ✅ `templates/dashboard.html` - Socket.IO connection fixed
- ✅ `docker-compose.yml` - PostgreSQL service removed, all DATABASE_URLs updated
- ✅ `main_app.py` - DATABASE_URL updated for standalone mode

### 4.4 Build and Start Docker Containers
```bash
# Build all containers (this may take 10-20 minutes)
docker-compose build

# Start all services
docker-compose up -d

# Check logs
docker-compose logs -f

# Press Ctrl+C to exit logs
```

### 4.5 Verify Running Containers
```bash
# Check all containers are running
docker-compose ps

# You should see all services in "Up" state:
# - sakshi-main-app
# - sakshi-detection-processor
# - sakshi-people-counter
# - sakshi-heatmap
# - sakshi-kitchen-compliance
# - sakshi-queue-monitor
# - sakshi-security-monitor
# - sakshi-shutter-monitor
```

---

## 🌐 Part 5: Access the Application

### 5.1 Open in Browser
```
Dashboard: http://13.200.138.25:5001/dashboard
Landing Page: http://13.200.138.25:5001/
```

### 5.2 Health Check
```bash
# Test from server
curl http://localhost:5001/health

# Expected response:
# {"status":"healthy","timestamp":"2025-10-24T..."}
```

---

## 🔧 Management Commands

### Start Services
```bash
docker-compose up -d
```

### Stop Services
```bash
docker-compose down
```

### Restart Services
```bash
docker-compose restart
```

### View Logs
```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f main-app
docker-compose logs -f detection-processor
```

### Rebuild After Code Changes
```bash
docker-compose down
docker-compose build
docker-compose up -d
```

### Check Container Status
```bash
docker-compose ps
```

### Access Container Shell
```bash
docker exec -it sakshi-main-app bash
```

---

## 📊 Database Management

### Access PostgreSQL
```bash
psql -h 127.0.0.1 -U postgres -d sakshi
# Password: Tneural01
```

### Common PostgreSQL Commands
```sql
-- List all tables
\dt

-- View detections
SELECT * FROM detections ORDER BY timestamp DESC LIMIT 10;

-- View people counter data
SELECT * FROM daily_footfall ORDER BY report_date DESC LIMIT 7;

-- Exit
\q
```

### Backup Database
```bash
pg_dump -h 127.0.0.1 -U postgres sakshi > backup_$(date +%Y%m%d).sql
```

### Restore Database
```bash
psql -h 127.0.0.1 -U postgres sakshi < backup_20251024.sql
```

---

## 🐛 Troubleshooting

### Issue: Containers can't connect to PostgreSQL
```bash
# Check PostgreSQL is running
sudo systemctl status postgresql

# Check if port 5432 is listening
sudo netstat -tulpn | grep 5432

# Check PostgreSQL logs
sudo tail -f /var/log/postgresql/postgresql-*-main.log

# Test connection from container
docker exec -it sakshi-main-app bash
apt-get update && apt-get install -y postgresql-client
psql -h 127.0.0.1 -U postgres -d sakshi
```

### Issue: Live feed not showing
```bash
# Check if containers are running
docker-compose ps

# Check main-app logs
docker-compose logs main-app

# Verify browser can access server
# Open browser console (F12) and check for errors

# Check if port 5001 is accessible
curl http://13.200.138.25:5001/health
```

### Issue: GPU not detected
```bash
# Check GPU from host
nvidia-smi

# Check GPU from container
docker exec -it sakshi-detection-processor nvidia-smi

# If not working, check docker runtime
docker info | grep -i runtime
```

### Issue: Out of disk space
```bash
# Check disk usage
df -h

# Remove unused Docker images
docker system prune -a

# Remove old logs
docker-compose down
sudo find /var/lib/docker/containers/ -type f -name "*.log" -delete
docker-compose up -d
```

### Issue: Port 5001 already in use
```bash
# Find process using port 5001
sudo lsof -i :5001

# Kill the process
sudo kill -9 <PID>

# Or change port in docker-compose.yml (not recommended)
```

---

## 🔄 Update Application

### Pull Latest Code
```bash
cd ~/Sakshi-21-OCT

# If using git
git pull origin main

# If using SCP
# Upload new files from local machine
```

### Rebuild and Restart
```bash
docker-compose down
docker-compose build
docker-compose up -d
```

---

## 📝 Configuration Files

### RTSP Camera Links
Edit camera streams in:
```bash
nano config/rtsp_links.txt
```

Format:
```
rtsp://camera-url, Camera Name, App1, App2, App3
```

Example:
```
rtsp://admin:password@192.168.1.100:554/stream, Store Main Entrance, PeopleCounter, Security
rtsp://admin:password@192.168.1.101:554/stream, Kitchen Area, KitchenCompliance
rtsp://admin:password@192.168.1.102:554/stream, Checkout Counter, QueueMonitor, Generic
```

After changing, restart:
```bash
docker-compose restart
```

---

## 🎯 Performance Optimization

### For CPU-Only Deployment
If you don't have GPU, remove GPU sections from `docker-compose.yml`:
```yaml
# Remove these lines from all processor services:
deploy:
  resources:
    reservations:
      devices:
        - driver: nvidia
          count: 1
          capabilities: [gpu]
```

### For Limited Resources
Reduce number of processors by commenting out services in `docker-compose.yml` that you don't need.

---

## 🔒 Security Best Practices

1. **Change Database Password**:
   ```bash
   sudo -u postgres psql -c "ALTER USER postgres WITH PASSWORD 'NewStrongPassword123';"
   # Update password in docker-compose.yml and main_app.py
   ```

2. **Restrict Security Group**:
   - Change source from `0.0.0.0/0` to your specific IP addresses

3. **Enable HTTPS** (optional):
   - Use nginx reverse proxy with Let's Encrypt SSL

4. **Regular Updates**:
   ```bash
   sudo apt update && sudo apt upgrade -y
   docker-compose pull
   docker-compose up -d
   ```

---

## 📞 Support

If you encounter issues:
1. Check logs: `docker-compose logs -f`
2. Check PostgreSQL: `sudo systemctl status postgresql`
3. Check network: `curl http://localhost:5001/health`
4. Check firewall: `sudo ufw status`
5. Check AWS Security Group settings

---

## ✅ Deployment Checklist

- [ ] PostgreSQL installed and running
- [ ] Database `sakshi` created
- [ ] Docker and Docker Compose installed
- [ ] Code uploaded to server
- [ ] Firewall configured (UFW)
- [ ] AWS Security Group configured
- [ ] Docker containers built and running
- [ ] Application accessible at http://13.200.138.25:5001/dashboard
- [ ] Live feeds working
- [ ] Database connections successful

---

**🎉 Congratulations! Your Sakshi.AI application is now deployed on EC2!**

Access your dashboard at: **http://13.200.138.25:5001/dashboard**

