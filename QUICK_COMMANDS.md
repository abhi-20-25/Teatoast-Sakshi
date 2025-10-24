# 🚀 Sakshi AI - Quick Commands Reference

## 📋 Daily Operations

### Start Everything
```bash
cd /home/abhijith/Sakshi-21-OCT
docker compose up -d
```

### Stop Everything
```bash
docker compose down
```

### Restart All Services
```bash
docker compose restart
```

### Restart Specific Service
```bash
docker compose restart people-counter-processor
docker compose restart kitchen-compliance-processor
docker compose restart queue-monitor-processor
docker compose restart main-app
```

---

## 📊 Monitoring

### Check Status
```bash
docker ps
docker compose ps
```

### View Logs (Real-time)
```bash
# All services
docker compose logs -f

# Specific service
docker logs sakshi-main-app -f
docker logs sakshi-people-counter -f
docker logs sakshi-kitchen-compliance -f
docker logs sakshi-queue-monitor -f
docker logs sakshi-postgres -f
```

### View Last 50 Lines of Logs
```bash
docker logs sakshi-main-app --tail 50
docker logs sakshi-people-counter --tail 50
```

### Check Container Resource Usage
```bash
docker stats
```

---

## 🔍 Health Checks

### Test All Services
```bash
curl http://localhost:5001/dashboard
curl http://localhost:5010/health
curl http://localhost:5015/health
curl http://localhost:5011/health
```

### Test Video Feeds
```bash
curl -I http://localhost:5001/video_feed/PeopleCounter/cam_bb76c76ddb
curl -I http://localhost:5001/video_feed/KitchenCompliance/cam_d77ace3828
curl -I http://localhost:5001/video_feed/QueueMonitor/cam_f948cba9d4
```

### Test Database Connection
```bash
docker exec -it sakshi-postgres psql -U postgres -c "SELECT 1;"
```

---

## 🔧 Troubleshooting

### Service Won't Start
```bash
# Check logs for errors
docker logs <container-name> --tail 100

# Remove and recreate
docker compose down
docker compose up -d <service-name>
```

### Clear Everything and Start Fresh
```bash
# WARNING: This deletes all data including database!
docker compose down -v
docker compose up -d
```

### Rebuild Containers (after code changes)
```bash
docker compose down
docker compose build --no-cache
docker compose up -d
```

### Fix Port Conflicts
```bash
# Find what's using the port
sudo netstat -tulpn | grep 5001
sudo lsof -i :5001

# Kill the process
sudo kill -9 <PID>
```

---

## 📸 Camera Management

### Test RTSP Stream with ffmpeg
```bash
ffmpeg -rtsp_transport tcp -i "rtsp://admin:cctv%231234@182.65.205.121:554/cam/realmonitor?channel=1&subtype=0" -frames:v 1 test.jpg
```

### Test Network Connectivity to Camera
```bash
ping 182.65.205.121
telnet 182.65.205.121 554
```

### Enable Placeholder Mode (if cameras offline)
1. Edit `docker-compose.yml`
2. Change `USE_PLACEHOLDER_FEED=false` to `true` for affected processors
3. Restart: `docker compose restart <processor-name>`

---

## 💾 Database Operations

### Access PostgreSQL Shell
```bash
docker exec -it sakshi-postgres psql -U postgres -d sakshi
```

### Common SQL Queries
```sql
-- Check recent detections
SELECT * FROM detections ORDER BY timestamp DESC LIMIT 10;

-- Check people counter data
SELECT * FROM daily_footfall ORDER BY report_date DESC LIMIT 7;

-- Check kitchen violations
SELECT * FROM kitchen_violations ORDER BY timestamp DESC LIMIT 10;

-- Check queue logs
SELECT * FROM queue_logs ORDER BY timestamp DESC LIMIT 10;
```

### Backup Database
```bash
docker exec sakshi-postgres pg_dump -U postgres sakshi > backup_$(date +%Y%m%d).sql
```

### Restore Database
```bash
cat backup_20251024.sql | docker exec -i sakshi-postgres psql -U postgres -d sakshi
```

---

## 🌐 Network & Access

### Allow Remote Access
```bash
# Allow port 5001 through firewall
sudo ufw allow 5001/tcp
sudo ufw reload
```

### Access from Browser
- **Local:** http://localhost:5001/dashboard
- **Remote:** http://YOUR_SERVER_IP:5001/dashboard

---

## 📁 File Locations

- **Config:** `/home/abhijith/Sakshi-21-OCT/config/rtsp_links.txt`
- **Models:** `/home/abhijith/Sakshi-21-OCT/models/`
- **Detections:** `/home/abhijith/Sakshi-21-OCT/static/detections/`
- **Docker Compose:** `/home/abhijith/Sakshi-21-OCT/docker-compose.yml`
- **Logs:** `docker logs <container-name>`

---

## 🔄 Update Code

### After Git Pull
```bash
cd /home/abhijith/Sakshi-21-OCT
git pull
docker compose down
docker compose build
docker compose up -d
```

---

## 🆘 Emergency Commands

### Stop All Containers Immediately
```bash
docker stop $(docker ps -q)
```

### Remove All Containers
```bash
docker rm $(docker ps -a -q)
```

### Clean Up Unused Docker Resources
```bash
docker system prune -a
```

### View System Resource Usage
```bash
htop
nvidia-smi  # GPU usage
df -h       # Disk usage
free -h     # Memory usage
```

---

## 📞 Support

**Documentation:** 
- DEPLOYMENT_STATUS.md - Full deployment details
- README.md - Project overview
- QUICKSTART.md - Initial setup guide

**Logs Location:**
```bash
cd /home/abhijith/Sakshi-21-OCT
docker compose logs
```

---

*Keep this file handy for daily operations!*

