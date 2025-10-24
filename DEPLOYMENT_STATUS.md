# 🚀 Sakshi AI Deployment Status

**Date:** October 24, 2025  
**Status:** ✅ **OPERATIONAL**

---

## 📊 Running Services

| Service | Container Name | Status | Port | Purpose |
|---------|---------------|--------|------|---------|
| PostgreSQL Database | sakshi-postgres | ✅ Healthy | 5433 | Data storage |
| Main Application | sakshi-main-app | ✅ Healthy | 5001 | Web Dashboard & API Gateway |
| People Counter | sakshi-people-counter | ✅ Running | 5010 | Footfall tracking |
| Kitchen Compliance | sakshi-kitchen-compliance | ✅ Running | 5015 | Kitchen monitoring |
| Queue Monitor | sakshi-queue-monitor | ✅ Running | 5011 | Queue analytics |

---

## 🎥 Active Cameras

### 1. Main Entrance - People Counter
- **RTSP URL:** `rtsp://admin:cctv#1234@182.65.205.121:554/cam/realmonitor?channel=1&subtype=0`
- **Channel ID:** cam_bb76c76ddb
- **Features:** Bidirectional footfall tracking (IN/OUT counts)
- **Model:** YOLOv8n on CUDA

### 2. Kitchen Camera - Kitchen Compliance  
- **RTSP URL:** `rtsp://admin:cctv#1234@182.65.205.121:554/cam/realmonitor?channel=10&subtype=0`
- **Channel ID:** cam_d77ace3828
- **Features:** 
  - Apron/Cap detection
  - Gloves detection
  - Uniform color compliance
  - Mobile phone detection
- **Models:** Custom apron-cap, gloves, YOLOv8n on CUDA

### 3. Queue Area - Queue Monitor
- **RTSP URL:** `rtsp://admin:cctv#1234@182.65.205.121:554/cam/realmonitor?channel=5&subtype=0`
- **Channel ID:** cam_f948cba9d4
- **Features:** Queue length monitoring, alerts, analytics
- **Model:** YOLOv8n on CUDA

---

## 🌐 Access Points

- **Dashboard:** http://localhost:5001/dashboard
- **Landing Page:** http://localhost:5001/
- **API Health Checks:**
  - Main App: http://localhost:5001/health
  - People Counter: http://localhost:5010/health
  - Kitchen Compliance: http://localhost:5015/health
  - Queue Monitor: http://localhost:5011/health

---

## 📁 Key Configuration Files

### docker-compose.yml
- **Services Configured:** 5 (postgres, main-app, people-counter, kitchen-compliance, queue-monitor)
- **Network Mode:** Host networking for processors, bridge for postgres
- **Database Connection:** localhost:5433
- **GPU Support:** Enabled for all processor containers

### config/rtsp_links.txt
```
rtsp://admin:cctv%231234@182.65.205.121:554/cam/realmonitor?channel=10&subtype=0, Kitchen Camera, KitchenCompliance
rtsp://admin:cctv%231234@182.65.205.121:554/cam/realmonitor?channel=1&subtype=0, Main Entrance, PeopleCounter
rtsp://admin:cctv%231234@182.65.205.121:554/cam/realmonitor?channel=5&subtype=0, QueueMonitor, QueueMonitor
```

---

## 🔧 System Configuration

### Database
- **Engine:** PostgreSQL 15-alpine
- **Connection:** postgresql+psycopg2://postgres:Tneural01@localhost:5433/sakshi
- **Tables Created:**
  - detections
  - kitchen_violations
  - daily_footfall
  - hourly_footfall
  - queue_logs
  - shutter_logs
  - security_violations
  - roi_configs

### Environment Variables
- `DOCKER_MODE=true` - Enables Docker microservice mode
- `USE_PLACEHOLDER_FEED=false` - Attempts real RTSP connections first
- `DATABASE_URL` - Points to localhost:5433
- Telegram credentials configured for notifications

---

## 🛠️ Common Management Commands

### Start Services
```bash
docker compose up -d
```

### Stop Services
```bash
docker compose down
```

### View Logs
```bash
# All logs
docker compose logs -f

# Specific service
docker logs sakshi-main-app -f
docker logs sakshi-people-counter -f
docker logs sakshi-kitchen-compliance -f
docker logs sakshi-queue-monitor -f
```

### Check Status
```bash
docker ps
docker compose ps
```

### Restart a Service
```bash
docker compose restart people-counter-processor
```

### View Real-time Stats
```bash
docker stats
```

---

## 🐛 Troubleshooting

### Issue: Video feeds not showing
**Solution:**
1. Check processor logs: `docker logs sakshi-people-counter --tail 50`
2. Verify RTSP connectivity: Test with VLC or ffmpeg
3. Check firewall: `sudo ufw allow 554/tcp`

### Issue: Database connection errors
**Solution:**
1. Verify postgres is healthy: `docker ps | grep postgres`
2. Check connection: `docker exec -it sakshi-postgres psql -U postgres -c "SELECT 1;"`

### Issue: Container keeps restarting
**Solution:**
1. Check logs: `docker logs <container-name> --tail 100`
2. Verify GPU is available: `nvidia-smi`
3. Check port conflicts: `sudo netstat -tulpn | grep <port>`

### Issue: RTSP stream timeout
**Solution:**
1. Verify camera IP is reachable: `ping 182.65.205.121`
2. Test RTSP URL: `ffmpeg -rtsp_transport tcp -i "<rtsp_url>" -frames:v 1 test.jpg`
3. Check camera credentials are correct

---

## 📈 Next Steps

### To Add More Cameras
1. Edit `config/rtsp_links.txt`
2. Add new line: `rtsp://url, Camera Name, AppName`
3. Restart services: `docker compose restart`

### To Enable Placeholder Mode (if RTSP unavailable)
1. Edit `docker-compose.yml`
2. Change `USE_PLACEHOLDER_FEED=false` to `true`
3. Restart processors: `docker compose restart people-counter-processor kitchen-compliance-processor queue-monitor-processor`

### To Access from Remote
1. Update firewall: `sudo ufw allow 5001/tcp`
2. Access via: `http://YOUR_SERVER_IP:5001/dashboard`

---

## ✅ Deployment Summary

**Total Containers:** 5  
**Active Cameras:** 3  
**GPU Utilization:** Enabled  
**Database:** PostgreSQL (Healthy)  
**Web Dashboard:** Operational  
**Video Streaming:** Active  
**Detection Systems:** Operational  

**System is fully operational and ready for use!** 🎉

---

*For support or issues, check logs and refer to troubleshooting section above.*

