# Server Deployment Guide - Complete Fix Package

## 🔧 Fixes Applied
- ✅ Added `openpyxl>=3.1.0` to requirements files
- ✅ Improved Excel time parsing to handle multiple formats
- ✅ **NEW: Added CSV file support** - Now accepts both .xlsx and .csv files
- ✅ **NEW: Optimized RTSP streaming** - Smooth, real-time playback (100 FPS)
- ✅ Fixed "0 time slots configured" issue
- ✅ Resolves "No module named 'openpyxl'" error
- ✅ PostgreSQL and detection image storage verified working
- ✅ Queue Monitor ROI/line settings persist to database

## 📝 What's Fixed
1. **OpenPyXL Missing**: Added dependency for Excel file reading
2. **Time Format Parsing**: Now handles datetime objects, time objects, and various string formats (9:00, 09:00, 09:00:00)
3. **CSV Support**: Can now upload schedules in both CSV and Excel formats
4. **Streaming Performance**: Reduced lag from 25-50 FPS to 100 FPS for smooth real-time video
5. **Cache Headers**: Added proper cache-control headers to prevent buffering
6. **Better Logging**: Shows how many time slots were successfully parsed
7. **Error Handling**: Improved error messages for debugging

## 📋 Quick Start (Automated Script)

The easiest way to update your server:

```bash
# Download and run the update script
cd /home/ubuntu/Sakshi-Teatoast-Fresh
git fetch origin
git checkout fix/openpyxl-postgresql-detection-images
git pull origin fix/openpyxl-postgresql-detection-images
chmod +x SERVER_UPDATE_COMMANDS.sh
./SERVER_UPDATE_COMMANDS.sh
```

Or follow the manual steps below:

---

## 📋 Manual Deployment Commands

### Step 1: Pull the Latest Changes

```bash
# Navigate to project directory
cd /path/to/Sakshi-21-OCT

# Fetch all branches
git fetch origin

# Checkout the fix branch
git checkout fix/openpyxl-postgresql-detection-images

# Pull latest changes
git pull origin fix/openpyxl-postgresql-detection-images
```

### Step 2: Stop Current Services

```bash
# Stop all running containers
docker-compose down
```

### Step 3: Rebuild Containers (IMPORTANT!)

```bash
# Remove old occupancy monitor image to force complete rebuild
docker rmi $(docker images | grep 'sakshi.*occupancy' | awk '{print $3}') 2>/dev/null || true

# Rebuild all containers with no cache
docker-compose build --no-cache

# Alternative: Rebuild only occupancy monitor if needed
# docker-compose build --no-cache occupancy-monitor-processor
```

### Step 4: Start Services

```bash
# Start all services
docker-compose up -d

# Check services are running
docker-compose ps
```

### Step 5: Verify OpenPyXL Installation

```bash
# Verify openpyxl is installed in the container
docker exec sakshi-occupancy-monitor pip list | grep openpyxl

# Expected output: openpyxl  3.1.x or higher
```

### Step 6: Check Logs

```bash
# Watch occupancy monitor logs
docker-compose logs -f occupancy-monitor-processor

# Check all service logs
docker-compose logs --tail=50
```

### Step 7: Test Schedule Upload (CSV or Excel)

1. Open browser: `http://your-server-ip:5001/dashboard`
2. Navigate to Occupancy Monitor section
3. Click "Upload Schedule (.xlsx or .csv)" 
4. Upload either a CSV or Excel file with your schedule
5. Verify you see: "X time slots configured" (not 0)
6. Both file formats (.csv and .xlsx) should work perfectly

---

## 🔄 Alternative: Quick Docker Fix (Temporary)

If you need immediate fix without full rebuild:

```bash
# Install openpyxl directly in running container
docker exec sakshi-occupancy-monitor pip install openpyxl

# Restart the container
docker-compose restart occupancy-monitor-processor
```

⚠️ **Note:** This temporary fix will be lost if container is recreated.

---

## 📊 Verification Checklist

- [ ] Branch pulled successfully
- [ ] Containers rebuilt with `--no-cache`
- [ ] All services running (`docker-compose ps` shows "Up")
- [ ] openpyxl installed (verified via `pip list`)
- [ ] Excel upload works without errors
- [ ] Detection images display in frontend
- [ ] PostgreSQL database connected

---

## 🗄️ PostgreSQL Configuration

The application is configured to use:
- **Database:** `sakshi`
- **User:** `postgres`
- **Port:** `5433` (external), `5432` (internal)
- **Connection:** Handled automatically via Docker network

Detection images are:
- Stored in: `/app/static/detections/` (inside containers)
- Mounted from: `./static/detections/` (on host)
- Served via Flask static files
- Paths saved to PostgreSQL `detections` table

---

## 🚨 Troubleshooting

### Issue: Still getting openpyxl error
```bash
# Force complete rebuild
docker-compose down -v
docker system prune -f
docker-compose build --no-cache
docker-compose up -d
```

### Issue: Images not showing in frontend
```bash
# Check static folder permissions
ls -la static/detections/

# Check database connection
docker exec sakshi-main-app python -c "from sqlalchemy import create_engine; engine = create_engine('postgresql+psycopg2://postgres:Tneural01@localhost:5433/sakshi'); print('DB Connected:', engine.connect())"
```

### Issue: PostgreSQL connection error
```bash
# Check PostgreSQL is running
docker-compose ps postgres

# Check PostgreSQL logs
docker-compose logs postgres

# Restart PostgreSQL
docker-compose restart postgres
```

---

## 📝 Notes

- This fix is on branch: `fix/openpyxl-postgresql-detection-images`
- Create a pull request to merge into main/production branch when verified
- The fix includes both `requirements.txt` and `config/requirements.txt`
- Docker automatically installs openpyxl during build (line 20 of Dockerfile.occupancy_monitor)

---

## 🔗 Useful Commands

```bash
# View all running containers
docker ps

# View all Docker images
docker images

# Access container shell
docker exec -it sakshi-occupancy-monitor bash

# View real-time logs
docker-compose logs -f --tail=100

# Restart specific service
docker-compose restart occupancy-monitor-processor

# Check disk usage
df -h

# Check Docker disk usage
docker system df
```

---

**Last Updated:** October 26, 2025
**Branch:** fix/openpyxl-postgresql-detection-images
**Repository:** https://github.com/abhi-20-25/Teatoast.git

