# Quick Reference Guide - Queue Monitor ROI & People Counter

## 🎯 Quick Visual Guide

### People Counter - Direction Logic

```
┌─────────────────────────────────────────┐
│                                         │
│    OUT <─ RIGHT          LEFT ─> IN    │
│                                         │
│         ←─────────│─────────→          │
│                   │                     │
│         Person    │    Person           │
│         Going     │    Going            │
│         LEFT      │    RIGHT            │
│         (OUT)     │    (IN)             │
│                   │                     │
│                   │ (Green Line)        │
│                   │                     │
└─────────────────────────────────────────┘
```

**Rule:** 
- Cross LEFT → Counted as **IN** ✅
- Cross RIGHT → Counted as **OUT** ✅

---

## 🎨 Edit ROI Feature - Quick Steps

### Step 1: Open Editor
```
Dashboard → Queue Monitor → "Edit ROI" button (top right)
```

### Step 2: Draw Main ROI (Queue Area)
```
1. Click "Draw Main" button
2. Click on video to place points
3. Draw around the queue waiting area
4. Polygon appears in YELLOW
```

### Step 3: Draw Secondary ROI (Counter Area)
```
1. Click "Draw Secondary" button  
2. Click on video to place points
3. Draw around the service counter
4. Polygon appears in CYAN
```

### Step 4: Save or Reset
```
- "Reset" → Clear current polygon
- "Cancel" → Exit without saving
- "Save" → Save to database & apply immediately
```

---

## 📊 Queue Monitor Logic

```
┌──────────────────────────────────────────┐
│  Camera View                             │
│                                          │
│  ╔════════════╗                         │
│  ║  QUEUE     ║  ← Main ROI (Yellow)    │
│  ║  👤👤👤     ║    Detects waiting      │
│  ║            ║    people               │
│  ╚════════════╝                         │
│                                          │
│  ┌──────┐                               │
│  │COUNTER│  ← Secondary ROI (Cyan)      │
│  │ 👤   │    Detects staff              │
│  └──────┘                               │
└──────────────────────────────────────────┘

ALERT TRIGGERS when:
- Queue Count > 2 people (in Main ROI for 3+ seconds)
- Counter Count ≤ 1 person (in Secondary ROI)
- Cooldown: 180 seconds between alerts
```

---

## 🎯 ROI Colors Reference

| Zone | Color | RGB | Purpose |
|------|-------|-----|---------|
| **Main ROI** | 🟨 Yellow | (255, 255, 0) | Queue waiting area |
| **Secondary ROI** | 🔵 Cyan | (0, 255, 255) | Service counter |
| **Main Boxes** | 🟨 Yellow | (255, 255, 0) | People in queue |
| **Secondary Boxes** | 🔵 Cyan | (0, 255, 255) | People at counter |

---

## 🔧 Configuration Values

### People Counter
```python
LINE_POSITION = 50%  # Middle of frame
CONFIDENCE = 0.5     # Detection confidence
IOU = 0.5           # Tracking IoU threshold
TRACK_HISTORY = 30   # Frames to keep
```

### Queue Monitor
```python
QUEUE_DWELL_TIME_SEC = 3.0        # Time to count as queuing
QUEUE_ALERT_THRESHOLD = 2         # People to trigger alert
QUEUE_ALERT_COOLDOWN_SEC = 180    # 3 minutes between alerts
CONFIDENCE = 0.4                   # Detection confidence
```

---

## 📁 Important Files & Paths

### Detection Storage
```
static/detections/
  ├── QueueMonitor_cam_xxxxx_20251024_123456.jpg
  ├── PeopleCounter_cam_xxxxx_20251024_123457.jpg
  └── ...
```

### Configuration
```
config/
  └── rtsp_links.txt  # Camera configuration
```

### Database Tables
```sql
roi_configs          # ROI polygon storage
detections          # Detection history
queue_logs          # Queue count logs
daily_footfall      # Daily IN/OUT counts
hourly_footfall     # Hourly IN/OUT counts
```

---

## 🌐 API Endpoints

### ROI Management
```
POST /api/set_roi
Body: {
  "app_name": "QueueMonitor",
  "channel_id": "cam_xxxxx",
  "roi_points": {
    "main": [[x1,y1], [x2,y2], ...],
    "secondary": [[x1,y1], [x2,y2], ...]
  }
}
```

### History
```
GET /history/QueueMonitor?page=1&limit=10&channel_id=cam_xxxxx
GET /history/PeopleCounter?page=1&limit=10&channel_id=cam_xxxxx
```

### Reports
```
GET /generate_report/{channel_id}?period=7days
GET /queue_report/{channel_id}?period=today
GET /report/{channel_id}/{date}
```

---

## 🔌 Socket.IO Events

### Emitted from Backend
```javascript
'count_update'      // { channel_id, in_count, out_count }
'queue_update'      // { channel_id, count }
'new_detection'     // { app_name, channel_id, timestamp, message, media_url }
```

### Connection
```javascript
// Auto-configures to current server
const socket = io(`http://${window.location.hostname}:5001`);
```

---

## 🚀 Starting the System

### Standard Mode
```bash
python main_app.py
```

### Docker Mode
```bash
docker-compose up -d
```

### Check Status
```bash
# View logs
tail -f logs/application.log

# Check processes
ps aux | grep python

# Docker status
docker-compose ps
```

---

## 🐛 Quick Troubleshooting

### ROI Not Visible
```javascript
// Check browser console
// Verify canvas element: document.querySelector('.roi-canvas')
// Check if active class applied: element.classList.contains('active')
```

### Direction Wrong
```
✅ Fixed! Left→IN, Right→OUT
   Visual labels now show on video feed
```

### Detection Not Saving
```bash
# Check static/detections/ folder permissions
ls -la static/detections/

# Verify database connection
# Check detections table
```

### Video Feed Not Loading
```
1. Check RTSP URL in config/rtsp_links.txt
2. Verify camera is reachable
3. Check processor is running: docker-compose ps
4. Test stream: ffplay rtsp://your-camera-url
```

---

## 📞 System Architecture

```
┌─────────────────────────────────────────────────┐
│                 Browser/Frontend                │
│  - dashboard.html (UI + ROI Drawing)            │
│  - Socket.IO client                             │
└─────────────────┬───────────────────────────────┘
                  │ HTTP/WebSocket
┌─────────────────▼───────────────────────────────┐
│              Main Application                    │
│  - Flask server (main_app.py)                   │
│  - API endpoints                                │
│  - Socket.IO server                             │
└──────┬──────────────────────────────┬───────────┘
       │                              │
       │                              │
┌──────▼──────────┐          ┌────────▼──────────┐
│   Processors    │          │   Database        │
│                 │          │   PostgreSQL      │
│ - PeopleCounter │◄────────►│   - roi_configs   │
│ - QueueMonitor  │          │   - detections    │
│ - Detection     │          │   - *_footfall    │
│ - Heatmap       │          │   - *_logs        │
└──────┬──────────┘          └───────────────────┘
       │
       │ RTSP/Video
┌──────▼──────────────────────────────────────────┐
│              Camera Streams                      │
│  - RTSP URLs from rtsp_links.txt                │
└──────────────────────────────────────────────────┘
```

---

## ✅ Feature Status

| Feature | Status | Notes |
|---------|--------|-------|
| People Counter Direction | ✅ Fixed | Left→IN, Right→OUT |
| Visual Direction Labels | ✅ Added | Shows on video feed |
| Queue ROI Edit | ✅ Working | Already implemented |
| ROI Draw Interface | ✅ Working | Canvas overlay + controls |
| ROI Persistence | ✅ Working | Database storage |
| Detection Saving | ✅ Working | Auto-saves on alert |
| Detection Display | ✅ Working | History grid + lightbox |
| Server IP Auto-config | ✅ Working | Uses window.location.hostname |

---

## 📚 Documentation Files

1. **ROI_EDITING_GUIDE.md** - Complete technical guide
2. **CHANGES_SUMMARY.md** - Summary of changes made
3. **QUICK_REFERENCE.md** - This file (quick lookup)

---

## 💡 Tips

### For Best Queue Detection:
- Draw Main ROI around entire queue area
- Draw Secondary ROI tightly around counter
- Ensure ROIs don't overlap
- Test with different crowd sizes

### For Best People Counter:
- Position camera perpendicular to traffic flow
- Ensure clear view of counting line
- Adjust confidence if too many/few detections
- Monitor false positives

### For Best Performance:
- Use H.264 RTSP streams
- Keep frame resolution ≤ 1080p
- Ensure good lighting
- Minimize camera motion

---

## 🎓 Key Concepts

**Normalized Coordinates:**
- ROI points stored as 0-1 range
- Independent of actual frame size
- Scales automatically with resolution

**Tracking:**
- YOLOv8 track IDs persist across frames
- Enables direction detection
- Enables dwell time calculation

**Dwell Time:**
- Person must stay 3+ seconds to count as queuing
- Prevents counting people passing through
- Reduces false alerts

**Alert Cooldown:**
- 3-minute minimum between queue alerts
- Prevents notification spam
- Configurable in processor

---

**Last Updated:** October 24, 2025
**Version:** 1.0

