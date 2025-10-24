# 🚀 Quick Start Guide - Sakshi.AI on EC2

## Prerequisites
- EC2 Ubuntu Server (13.200.138.25)
- Sudo access

---

## Step 1: Install PostgreSQL

Run the automated setup script:

```bash
cd ~/Sakshi-21-OCT
./setup_postgres.sh
```

This will:
- ✅ Install PostgreSQL
- ✅ Create `sakshi` database
- ✅ Configure database user
- ✅ Set up TCP connections
- ✅ Test the connection

**Expected Output:** "Connection successful!"

---

## Step 2: Install Docker & Docker Compose

```bash
# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER

# Log out and back in
exit
# SSH back to server

# Install Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Verify
docker --version
docker-compose --version
```

---

## Step 3: Configure Firewall

```bash
# Enable firewall
sudo ufw enable

# Allow necessary ports
sudo ufw allow 22/tcp    # SSH
sudo ufw allow 5001/tcp  # Sakshi.AI

# Check status
sudo ufw status
```

**Also configure AWS Security Group:**
- EC2 Console → Security Groups
- Add Inbound Rule: Port 5001, TCP, Source: 0.0.0.0/0

---

## Step 4: Configure Camera Streams

Edit the RTSP links file:

```bash
nano config/rtsp_links.txt
```

Add your camera URLs:
```
rtsp://admin:password@192.168.1.100:554/stream, Main Entrance, PeopleCounter, Security
rtsp://admin:password@192.168.1.101:554/stream, Kitchen Area, KitchenCompliance
rtsp://admin:password@192.168.1.102:554/stream, Checkout Counter, QueueMonitor
```

---

## Step 5: Deploy Application

Use the automated deployment script:

```bash
cd ~/Sakshi-21-OCT
./deploy.sh
```

Select option **1** (Deploy)

This will:
- ✅ Build Docker images
- ✅ Start all services
- ✅ Show service status

**Wait Time:** 10-20 minutes for first build

---

## Step 6: Access Dashboard

Open in browser:
```
http://13.200.138.25:5001/dashboard
```

---

## Common Commands

### View Logs
```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f main-app
```

### Check Status
```bash
docker-compose ps
```

### Restart Services
```bash
docker-compose restart
```

### Stop Services
```bash
docker-compose down
```

### Rebuild After Changes
```bash
docker-compose down
docker-compose build
docker-compose up -d
```

---

## Troubleshooting

### Live feed not showing?
1. Check if containers are running: `docker-compose ps`
2. Check main-app logs: `docker-compose logs main-app`
3. Clear browser cache and reload

### Can't connect to database?
```bash
# Check PostgreSQL
sudo systemctl status postgresql

# Test connection
PGPASSWORD='Tneural01' psql -h 127.0.0.1 -U postgres -d sakshi
```

### Port 5001 not accessible?
```bash
# Check firewall
sudo ufw status

# Check if port is listening
sudo netstat -tulpn | grep 5001
```

---

## Service Ports

| Service | Port |
|---------|------|
| Web Dashboard | 5001 |
| PostgreSQL | 5432 (localhost only) |

---

## Support

For detailed documentation, see:
- `DEPLOYMENT_EC2.md` - Complete deployment guide
- `README.md` - Project documentation

---

**🎉 That's it! Your Sakshi.AI is now running!**

Dashboard URL: **http://13.200.138.25:5001/dashboard**

