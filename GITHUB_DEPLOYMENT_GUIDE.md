# GitHub Deployment Guide for Sakshi-Teatoast Project

## Repository Information
- **GitHub URL**: https://github.com/abhi-20-25/Teatoast-Sakshi.git
- **Branch**: main

---

## 📋 Prerequisites on Server

Before deploying, ensure your server has:
- Ubuntu/Debian Linux (18.04 or later)
- Docker and Docker Compose installed
- Git installed
- Sudo/root access
- NVIDIA GPU with drivers installed (for GPU support)
- Open ports: 5000, 5001, 5002

---

## 🚀 Deployment Steps on Server

### Step 1: Clone the Repository

```bash
# Navigate to your desired installation directory
cd /home/ubuntu  # or your preferred location

# Clone the repository
git clone https://github.com/abhi-20-25/Teatoast-Sakshi.git

# Enter the project directory
cd Teatoast-Sakshi
```

### Step 2: Set Up Configuration Files

```bash
# Create the rtsp_links.txt configuration file
nano config/rtsp_links.txt
```

Add your RTSP camera links in the following format:
```
TeaToast001,rtsp://username:password@camera-ip:port/stream
TeaToast002,rtsp://username:password@camera-ip:port/stream
# Add more cameras as needed
```

**Save and exit** (Ctrl+X, then Y, then Enter)

### Step 3: Create Python Virtual Environment

```bash
# Install Python 3 and venv if not already installed
sudo apt update
sudo apt install -y python3 python3-venv python3-pip

# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate

# Upgrade pip
pip install --upgrade pip

# Install Python dependencies
pip install -r requirements.txt
```

### Step 4: Set Up Occupancy Schedule (Optional)

If you need the occupancy monitoring feature:

```bash
# Create or edit the occupancy schedule CSV file
nano test_occupancy_schedule.csv
```

Follow the template format in `occupancy_schedule_template.csv`.

### Step 5: Install Docker and Docker Compose (if not installed)

```bash
# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Add your user to docker group
sudo usermod -aG docker $USER

# Install Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Verify installations
docker --version
docker-compose --version

# Log out and log back in for group changes to take effect
```

### Step 6: Start the Application with Docker

```bash
# Make deployment scripts executable
chmod +x docker-start.sh docker-stop.sh docker-status.sh docker-logs.sh

# Start all services using Docker Compose
./docker-start.sh

# Or manually:
docker-compose up -d
```

### Step 7: Verify Deployment

```bash
# Check service status
./docker-status.sh

# Or manually:
docker-compose ps

# View logs
./docker-logs.sh

# Or view specific service logs:
docker-compose logs -f person_detection
docker-compose logs -f queue_monitor
docker-compose logs -f occupancy_monitor
```

### Step 8: Access the Applications

- **Person Detection & Streaming**: http://your-server-ip:5000
- **Queue Management System**: http://your-server-ip:5001
- **Occupancy Monitoring System**: http://your-server-ip:5002

---

## 🔄 Updating the Code (Pull Latest Changes)

When updates are pushed to GitHub:

```bash
# Navigate to project directory
cd /home/ubuntu/Teatoast-Sakshi  # or your installation path

# Stop running services
./docker-stop.sh

# Pull latest changes from GitHub
git pull origin main

# Rebuild Docker images (if Dockerfiles changed)
docker-compose build

# Restart services
./docker-start.sh
```

---

## 🛠️ Alternative: Running Without Docker

If you prefer to run without Docker:

### Option 1: Run All Services Together

```bash
# Activate virtual environment
source venv/bin/activate

# Run the main application
python main_app.py
```

### Option 2: Run Individual Services

**Terminal 1 - Person Detection:**
```bash
source venv/bin/activate
python run.py
```

**Terminal 2 - Queue Monitor:**
```bash
source venv/bin/activate
cd services
python queue_monitor_service.py
```

**Terminal 3 - Occupancy Monitor:**
```bash
source venv/bin/activate
python -c "from processors.occupancy_monitor_processor import OccupancyMonitorProcessor; import asyncio; asyncio.run(OccupancyMonitorProcessor().run())"
```

---

## 📊 Service Ports

| Service | Port | URL |
|---------|------|-----|
| Person Detection | 5000 | http://server-ip:5000 |
| Queue Monitor | 5001 | http://server-ip:5001 |
| Occupancy Monitor | 5002 | http://server-ip:5002 |

---

## 🔧 Troubleshooting

### Issue: Permission Denied on Docker

```bash
# Add user to docker group
sudo usermod -aG docker $USER
# Log out and log back in
```

### Issue: Port Already in Use

```bash
# Check what's using the port
sudo lsof -i :5000  # replace with your port

# Stop the process or change port in docker-compose.yml
```

### Issue: RTSP Stream Not Working

1. Verify camera IP and credentials in `config/rtsp_links.txt`
2. Test RTSP stream with VLC or ffmpeg
3. Check network connectivity to cameras
4. Ensure firewall allows RTSP connections

### Issue: GPU Not Detected

```bash
# Check NVIDIA driver installation
nvidia-smi

# If not installed, install NVIDIA drivers
sudo ubuntu-drivers autoinstall
sudo reboot
```

### Issue: Out of Memory

```bash
# Reduce number of concurrent camera streams
# Edit config/rtsp_links.txt and comment out some cameras

# Or increase swap space
sudo fallocate -l 4G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile
```

---

## 📝 Important Configuration Files

1. **config/rtsp_links.txt** - Camera RTSP URLs (create this manually)
2. **test_occupancy_schedule.csv** - Occupancy schedule
3. **docker-compose.yml** - Docker service configuration
4. **requirements.txt** - Python dependencies

---

## 🔐 Security Best Practices

1. **Never commit RTSP credentials to GitHub**
   - The `config/rtsp_links.txt` is in .gitignore
   - Always create this file manually on the server

2. **Use strong passwords** for camera authentication

3. **Configure firewall** to restrict access:
```bash
sudo ufw allow 5000/tcp
sudo ufw allow 5001/tcp
sudo ufw allow 5002/tcp
sudo ufw enable
```

4. **Use HTTPS** in production with reverse proxy (nginx/apache)

---

## 📚 Additional Documentation

- **OCCUPANCY_MONITOR_SETUP.md** - Detailed occupancy monitor setup
- **SERVER_DEPLOYMENT_OPENPYXL_FIX.md** - Excel file handling fixes
- **DEPLOYMENT_QUEUE_FIX.md** - Queue management deployment
- **SMOOTH_STREAMING_FINAL.md** - Streaming optimization guide

---

## 🆘 Support & Maintenance

### View Application Logs
```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f person_detection
docker-compose logs -f queue_monitor
docker-compose logs -f occupancy_monitor
```

### Restart Services
```bash
./docker-stop.sh
./docker-start.sh
```

### Clean Up Docker Resources
```bash
# Remove stopped containers
docker-compose down

# Remove all unused resources
docker system prune -a
```

---

## 📞 Quick Command Reference

```bash
# Clone repository
git clone https://github.com/abhi-20-25/Teatoast-Sakshi.git

# Update code
cd Teatoast-Sakshi && git pull origin main

# Start services
./docker-start.sh

# Stop services
./docker-stop.sh

# Check status
./docker-status.sh

# View logs
./docker-logs.sh

# Restart specific service
docker-compose restart person_detection
```

---

## ✅ Post-Deployment Checklist

- [ ] Repository cloned successfully
- [ ] config/rtsp_links.txt created with camera URLs
- [ ] Virtual environment created and activated
- [ ] Dependencies installed from requirements.txt
- [ ] Docker and Docker Compose installed
- [ ] Services started with docker-compose
- [ ] All three web interfaces accessible
- [ ] Camera streams visible in web UI
- [ ] Logs show no critical errors
- [ ] Firewall configured (if applicable)
- [ ] Backup of configuration files created

---

**Last Updated**: October 27, 2025
**Repository**: https://github.com/abhi-20-25/Teatoast-Sakshi.git

