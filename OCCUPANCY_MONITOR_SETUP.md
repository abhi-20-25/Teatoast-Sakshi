# Live Occupancy Monitor - Setup Guide

## ✅ What Was Implemented

The **Live Occupancy Monitor** feature has been successfully added to your Sakshi application. This feature monitors RTSP camera feeds, detects people in real-time using YOLO, compares live counts against scheduled requirements, and sends alerts when counts fall below requirements.

## 📁 Files Created

1. **`processors/occupancy_monitor_processor.py`** - Main processor with YOLO detection and scheduling logic
2. **`services/occupancy_monitor_service.py`** - Microservice that runs the processor
3. **`docker/Dockerfile.occupancy_monitor`** - Docker container configuration

## 📝 Files Modified

1. **`docker-compose.yml`** - Added occupancy-monitor-processor service
2. **`main_app.py`** - Added 3 new API routes and configuration
3. **`templates/dashboard.html`** - Added frontend UI with charts and upload functionality
4. **`config/rtsp_links.txt`** - Added OccupancyMonitor to available apps list

## 🚀 How to Start the Container

### Build and Start the Container

```bash
# Build the new container
docker-compose build occupancy-monitor-processor

# Start all services (including the new one)
docker-compose up -d

# Or start just the occupancy monitor
docker-compose up -d occupancy-monitor-processor

# Check logs
docker-compose logs -f occupancy-monitor-processor
```

## 📊 How to Use

### 1. Enable OccupancyMonitor on a Camera

Edit `config/rtsp_links.txt` and add `OccupancyMonitor` to any camera line:

```
rtsp://admin:cctv%231234@182.65.205.121:554/cam/realmonitor?channel=1&subtype=0, Main Entrance, PeopleCounter, OccupancyMonitor
```

### 2. Restart the Container

```bash
docker-compose restart occupancy-monitor-processor
```

### 3. Upload Schedule via Dashboard

1. Open the Sakshi dashboard at `http://localhost:5001/dashboard`
2. Find the **Occupancy Monitor** section
3. Click on the camera tab you want to configure
4. Upload an Excel file (.xlsx) with this format:

| Time  | Monday | Tuesday | Wednesday | Thursday | Friday | Saturday | Sunday |
|-------|--------|---------|-----------|----------|--------|----------|--------|
| 9:00  | 5      | 5       | 5         | 5        | 5      | 3        | 2      |
| 10:00 | 8      | 8       | 8         | 8        | 8      | 5        | 3      |
| 11:00 | 10     | 10      | 10        | 10       | 10     | 8        | 5      |

**Format Rules:**
- Row 1: Headers (Time, Monday, Tuesday, Wednesday, Thursday, Friday, Saturday, Sunday)
- Column A: Time in "H:00" format (e.g., 9:00, 10:00, 11:00)
- Other columns: Required number of people for that day/time

### 4. Monitor Live Feed

The dashboard will show:
- **Live Feed** - Video with detected people highlighted in green boxes
- **Live Count** - Current number of people detected
- **Required Count** - Expected number from schedule
- **Status** - OK or Below Requirement
- **Alert Banner** - Red banner appears when count is below requirement

### 5. View Reports

Click on report buttons to view:
- **Today** - Today's occupancy data
- **Yesterday** - Yesterday's full report
- **Last 7 Days** - Weekly trend analysis

Reports include:
- Total records analyzed
- Number of alerts triggered
- Compliance rate (% of time requirements were met)
- Average live count vs average required count
- Interactive chart showing live vs required counts over time

## 🔧 Configuration

### Alert Settings

In `processors/occupancy_monitor_processor.py`, you can adjust:

```python
self.alert_cooldown = 300  # 5 minutes between alerts (line 65)
detection_interval = 90     # Detection every 90 frames ~3 seconds (line 245)
```

### Detection Confidence

The processor filters detections at 50% confidence:

```python
if cls == 0 and conf > 0.5:  # Adjust 0.5 as needed (line 151)
```

## 📱 Telegram Notifications

Alerts are automatically sent to Telegram when:
- Live count < Required count
- Alert cooldown period has passed (default: 5 minutes)

Message format:
```
⚠️ OCCUPANCY ALERT - Camera Name
Time: 10:00 (Monday)
Required: 8 people
Detected: 5 people
Shortage: 3 people
```

## 🗄️ Database Tables

Two PostgreSQL tables are created automatically:

1. **`occupancy_logs`** - Stores every detection check
   - `id`, `channel_id`, `timestamp`, `time_slot`, `day_of_week`
   - `live_count`, `required_count`, `status`

2. **`occupancy_schedules`** - Stores schedule requirements
   - `id`, `channel_id`, `time_slot`, `day_of_week`, `required_count`

## 🐛 Troubleshooting

### Container won't start
```bash
# Check logs
docker-compose logs occupancy-monitor-processor

# Common issues:
# - Database not ready: Wait 30 seconds and retry
# - Model not found: Ensure yolov8n.pt exists in models/
```

### Schedule upload fails
- Ensure Excel file has correct format (Time column + day columns)
- Check file is .xlsx (not .xls)
- Verify time format is "9:00" not "9:00 AM"

### No detections appearing
- Verify RTSP stream is accessible
- Check camera has OccupancyMonitor in rtsp_links.txt
- Ensure container is running: `docker ps | grep occupancy`

### Video feed not showing
- Verify port 5017 is accessible
- Check main-app is proxying requests correctly
- Test direct access: `curl http://localhost:5017/health`

## 🌐 API Endpoints

The feature exposes these endpoints:

- `GET /occupancy_report/<channel_id>?period=today` - Get report data
- `GET /occupancy_schedule/<channel_id>` - Get current schedule
- `POST /api/upload_occupancy_schedule/<channel_id>` - Upload Excel schedule
- `GET /video_feed/OccupancyMonitor/<channel_id>` - Video stream
- `GET http://localhost:5017/health` - Container health check

## 📦 Dependencies

The feature uses existing dependencies:
- **ultralytics** (YOLO) - Already in requirements.txt
- **openpyxl** - Added to Dockerfile
- **opencv-python** - Already in requirements.txt
- **PostgreSQL** - Existing database
- **Chart.js** - Already loaded in dashboard

## ✨ Features Summary

✅ **RTSP Camera Support** - Uses existing camera streams  
✅ **YOLO Person Detection** - Real-time people counting  
✅ **Excel Schedule Upload** - Easy schedule management  
✅ **PostgreSQL Storage** - Persistent data storage  
✅ **Real-time Alerts** - Via Telegram and dashboard  
✅ **Historical Reports** - Charts and statistics  
✅ **Docker Container** - Isolated microservice  
✅ **Multi-camera Support** - Multiple channels simultaneously  
✅ **SocketIO Updates** - Live dashboard updates  

## 🎯 Next Steps

1. Add a camera to rtsp_links.txt with OccupancyMonitor
2. Build and start the container
3. Upload a schedule via the dashboard
4. Monitor live feed and receive alerts!

---

**Need help?** Check the logs: `docker-compose logs -f occupancy-monitor-processor`

