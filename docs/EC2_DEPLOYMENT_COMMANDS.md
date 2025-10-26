# EC2 Deployment Commands - CPU-Only with Frontend Fixes

## 🚀 Complete Deployment Steps for EC2

Run these commands on your EC2 instance to deploy the latest changes.

---

## Step 1: Stop Current Services

```bash
cd /home/ubuntu/Sakshi-Teatoast
docker-compose down -v
```

---

## Step 2: Pull Latest Changes from GitHub

```bash
cd /home/ubuntu/Sakshi-Teatoast
git pull origin frontend-fixes-oct-24
```

**Expected Output:**
```
From github.com:abhi-20-25/Sakshi-Teatoast
 * branch            frontend-fixes-oct-24 -> FETCH_HEAD
Updating 09193f5..0505ac7
Fast-forward
 docker-compose.yml | 45 ++++++++++++++++++++++++---------------------
 1 file changed, 24 insertions(+), 21 deletions(-)
```

---

## Step 3: Verify Changes

Check that GPU sections are commented out:

```bash
grep -A 5 "# GPU disabled" /home/ubuntu/Sakshi-Teatoast/docker-compose.yml
```

Check that Socket.IO uses explicit port:

```bash
grep "const socket = io" /home/ubuntu/Sakshi-Teatoast/templates/dashboard.html
```

**Should show:**
```javascript
const socket = io(`http://${window.location.hostname}:5001`);
```

---

## Step 4: Rebuild Docker Images

```bash
cd /home/ubuntu/Sakshi-Teatoast
docker-compose build --no-cache
```

---

## Step 5: Start All Services

```bash
docker-compose up -d
```

---

## Step 6: Verify All Services are Running

```bash
docker-compose ps
```

**Expected Output (all should show "Up"):**
```
NAME                        STATUS
sakshi-main-app            Up (healthy)
sakshi-postgres            Up (healthy)
sakshi-people-counter      Up (healthy)
sakshi-queue-monitor       Up (healthy)
sakshi-kitchen-compliance  Up (healthy)
```

---

## Step 7: Check Logs for Errors

```bash
# Check all logs
docker-compose logs -f

# Or check individual services
docker-compose logs main-app
docker-compose logs people-counter-processor
docker-compose logs queue-monitor-processor
docker-compose logs kitchen-compliance-processor
```

**Look for:**
- ✅ "Video processor initialized successfully"
- ✅ "Health endpoint ready"
- ✅ "Connected to database"
- ❌ No "CUDA" or "nvidia" errors

---

## Step 8: Test Health Endpoints

```bash
# Test main app
curl http://localhost:5001/health

# Test people counter processor
curl http://localhost:5010/health

# Test queue monitor processor
curl http://localhost:5011/health

# Test kitchen compliance processor
curl http://localhost:5015/health
```

**Expected Response (for each):**
```json
{
  "status": "healthy",
  "alive_count": 1,
  "timestamp": "2025-10-24T..."
}
```

---

## Step 9: Access the Dashboard

### Get Your EC2 Public IP:
```bash
curl http://169.254.169.254/latest/meta-data/public-ipv4
```

### Open in Browser:
```
http://YOUR_EC2_PUBLIC_IP:5001/dashboard
```

---

## Step 10: Verify Frontend

1. **Open Browser Developer Tools (F12)**
2. **Go to Console Tab**
3. **Look for:**
   ```
   ✅ Socket.IO connected successfully
   ```

4. **Check Network Tab:**
   - Should see video feed requests to `/video_feed/...`
   - Should see Socket.IO connection established

---

## 🔧 Troubleshooting

### If No Video Feed:

1. **Check if cameras/videos are configured:**
   ```bash
   cat /home/ubuntu/Sakshi-Teatoast/config/rtsp_links.txt
   ```

2. **Test with a sample video:**
   ```bash
   # Add this line to rtsp_links.txt
   test-videos/sample.mp4, Test Camera, PeopleCounter
   ```

3. **Check processor logs:**
   ```bash
   docker-compose logs people-counter-processor | grep -i error
   ```

### If Services Won't Start:

1. **Check for port conflicts:**
   ```bash
   sudo netstat -tlnp | grep -E '5001|5010|5011|5015|5433'
   ```

2. **Check disk space:**
   ```bash
   df -h
   ```

3. **Check memory:**
   ```bash
   free -h
   ```

### If Database Errors:

1. **Check PostgreSQL:**
   ```bash
   docker-compose logs postgres
   ```

2. **Verify connection:**
   ```bash
   docker exec -it sakshi-postgres psql -U postgres -d sakshi -c "SELECT COUNT(*) FROM detections;"
   ```

---

## 📊 Monitoring Commands

### Real-time Resource Usage:
```bash
docker stats
```

### Watch Service Status:
```bash
watch -n 2 'docker-compose ps'
```

### Follow All Logs:
```bash
docker-compose logs -f --tail=50
```

---

## 🎯 Key Changes Deployed

### 1. GPU Disabled ✅
- All NVIDIA GPU requirements commented out
- Services run on CPU only
- Compatible with standard EC2 instances

### 2. Frontend Socket.IO Fixed ✅
- Explicit port 5001 configuration
- Connection monitoring added
- Better error handling

### 3. Docker-Compose Optimized ✅
- Host networking mode
- Proper health checks
- Restart policies configured

---

## 🔄 Quick Restart Command

If you need to restart services quickly:

```bash
cd /home/ubuntu/Sakshi-Teatoast && docker-compose restart
```

---

## 🛑 Complete Cleanup (if needed)

To start completely fresh:

```bash
cd /home/ubuntu/Sakshi-Teatoast
docker-compose down -v
docker system prune -af --volumes
git pull origin frontend-fixes-oct-24
docker-compose build --no-cache
docker-compose up -d
```

---

## ✅ Success Checklist

- [ ] All services showing "Up (healthy)" in `docker-compose ps`
- [ ] Health endpoints responding (5001, 5010, 5011, 5015)
- [ ] Dashboard loads at http://EC2_IP:5001/dashboard
- [ ] Browser console shows "Socket.IO connected successfully"
- [ ] Video feeds visible on dashboard
- [ ] No errors in `docker-compose logs`
- [ ] PostgreSQL database accessible

---

## 📞 Support

If you encounter any issues:

1. Check logs: `docker-compose logs [service-name]`
2. Verify configuration: `cat config/rtsp_links.txt`
3. Test health endpoints: `curl http://localhost:5001/health`
4. Check resource usage: `docker stats`

---

**Deployment Date:** October 24, 2025  
**Branch:** frontend-fixes-oct-24  
**Mode:** CPU-only (GPU disabled)  
**Port:** 5001

