# Queue Monitor - Edit ROI Feature Guide

## Overview
The Edit ROI (Region of Interest) feature allows you to define two zones for Queue Monitoring:
1. **Main ROI (Yellow)** - The queue area where people wait
2. **Secondary ROI (Cyan)** - The counter/service area

## How It Works - Complete Flow

### 1. **Backend Processing** (`processors/queue_monitor_processor.py`)

The processor tracks people in two defined regions:

```
Main ROI (Yellow) = Queue Area
- Tracks people who stay for > 3 seconds (QUEUE_DWELL_TIME_SEC)
- Counts valid queue length
- Triggers alert if queue is full but counter is free

Secondary ROI (Cyan) = Counter Area  
- Tracks people at the service counter
- Used to determine if counter staff is available
```

**Detection Logic:**
- Person's bottom-center point is checked against both ROIs
- If in Main ROI for 3+ seconds → counted in queue
- If in Secondary ROI → counter is occupied
- **Alert Condition:** Queue > 2 people AND Counter ≤ 1 person

### 2. **Frontend Interface** (`templates/dashboard.html`)

#### Components:
```html
1. Edit ROI Button (only visible for QueueMonitor)
   - Located in filter-controls section
   - Triggers ROI drawing mode

2. Canvas Overlay (transparent layer over video)
   - Hidden by default
   - Becomes visible when editing
   - Captures click events for drawing

3. ROI Controls (Draw Main, Draw Secondary, Reset, Cancel, Save)
   - Hidden by default (.roi-controls)
   - Becomes active when editing
```

## Step-by-Step Usage Guide

### Opening ROI Editor

1. **Navigate to Queue Monitor** in the dashboard
2. **Click "Edit ROI" button** (top-right in filter controls)

**What happens:**
```javascript
- Canvas overlay appears over the video feed
- ROI control buttons become visible
- Drawing state initializes: { main: [], secondary: [] }
- Default mode: 'main' polygon
```

### Drawing ROIs

#### Drawing the Main ROI (Queue Area):

1. **Click "Draw Main" button** (if not already selected)
2. **Click on video to add points**
   - Each click adds a point to the polygon
   - Points appear as small circles
   - Lines connect sequential points
   - Polygon auto-closes after 3+ points
3. **Draw around the queue area** where people wait

**Visual Feedback:**
- Yellow stroke: `rgba(255, 255, 0, 0.8)` (bright yellow)
- Yellow fill: `rgba(255, 255, 0, 0.2)` (transparent yellow)
- Point circles: 4px radius

#### Drawing the Secondary ROI (Counter Area):

1. **Click "Draw Secondary" button** to switch mode
2. **Click on video to add points**
3. **Draw around the counter/service area**

**Visual Feedback:**
- Cyan stroke: `rgba(0, 255, 255, 0.8)` (bright cyan)
- Cyan fill: `rgba(0, 255, 255, 0.2)` (transparent cyan)

### Control Buttons

**Reset:**
- Clears points for currently selected polygon only
- If "Draw Main" is active → clears main points
- If "Draw Secondary" is active → clears secondary points

**Cancel:**
- Exits ROI editing mode
- Discards all changes
- Hides canvas and controls
- Returns to normal view

**Save:**
- Normalizes coordinates (0-1 range relative to canvas size)
- Sends to backend API: `POST /api/set_roi`
- Stores in database (`roi_configs` table)
- Updates live processor with new ROI
- Shows success/error alert
- Closes editing mode on success

## Technical Flow

### 1. Drawing Process

```javascript
handleCanvasClick(event, appName, channelId) {
  // Get click coordinates relative to canvas
  const rect = canvas.getBoundingClientRect();
  const x = event.clientX - rect.left;
  const y = event.clientY - rect.top;
  
  // Add to current polygon (main or secondary)
  state.points[state.currentPoly].push({ x, y });
  
  // Redraw canvas
  redrawRoiCanvas();
}
```

### 2. Coordinate Normalization

```javascript
// Convert pixel coordinates to normalized (0-1) range
normalizedPoints = {
  main: state.points.main.map(p => [
    p.x / canvas.width,   // x: 0-1
    p.y / canvas.height   // y: 0-1
  ]),
  secondary: state.points.secondary.map(p => [
    p.x / canvas.width,
    p.y / canvas.height
  ])
}
```

**Why normalize?**
- Video resolution may change
- Canvas size may vary
- Coordinates work across different display sizes

### 3. Backend Save Process

**API Endpoint:** `/api/set_roi`

```python
# 1. Save to database
INSERT INTO roi_configs (channel_id, app_name, roi_points)
VALUES (:channel_id, 'QueueMonitor', :json_roi_points)
ON CONFLICT (channel_id, app_name) 
DO UPDATE SET roi_points = EXCLUDED.roi_points;

# 2. Update live processor
processor.update_roi(roi_points)
  → normalized_main_roi = roi_points['main']
  → normalized_secondary_roi = roi_points['secondary']
  → _recalculate_polygons()  # Convert to pixel coordinates

# 3. Create Shapely Polygons for detection
roi_poly = Polygon([(x*frame_width, y*frame_height) for x,y in normalized_main_roi])
secondary_roi_poly = Polygon([(x*frame_width, y*frame_height) for x,y in normalized_secondary_roi])
```

### 4. Detection with ROI

```python
# For each detected person
person_point = Point(center_x, bottom_y)

# Check if in Main ROI
is_in_main = roi_poly.contains(person_point)
if is_in_main:
    # Track entry time
    # Count if stayed > 3 seconds
    
# Check if in Secondary ROI  
is_in_secondary = secondary_roi_poly.contains(person_point)
if is_in_secondary:
    # Counter is occupied
```

## ROI Persistence

### On Startup:
```python
# main_app.py - start_streams()
with SessionLocal() as db:
    roi_record = db.query(RoiConfig)
        .filter_by(channel_id=channel_id, app_name='QueueMonitor')
        .first()
    
    if roi_record:
        processor.update_roi(json.loads(roi_record.roi_points))
```

### Storage Format (Database):
```json
{
  "main": [
    [0.25, 0.30],
    [0.75, 0.30],
    [0.75, 0.80],
    [0.25, 0.80]
  ],
  "secondary": [
    [0.15, 0.15],
    [0.35, 0.15],
    [0.35, 0.35],
    [0.15, 0.35]
  ]
}
```

## Visual Feedback on Live Feed

The processed video shows:
- Yellow boxes around people in Main ROI
- Cyan boxes around people in Secondary ROI
- Yellow polygon outline for Main ROI
- Cyan polygon outline for Secondary ROI
- Queue count: "Queue: X"
- Counter status: "Counter Area: Y"

## Best Practices

### Drawing Tips:
1. **Main ROI (Queue):**
   - Draw around the typical queue formation area
   - Include entire waiting zone
   - Avoid including counter area
   - 4-6 points usually sufficient

2. **Secondary ROI (Counter):**
   - Draw tightly around counter/service point
   - Should be small and specific
   - Only where staff stands to serve

### Common Issues:

**ROI not appearing:**
- Check if canvas width/height is set correctly
- Verify points array has 3+ points
- Ensure drawing mode is active

**Detection not working:**
- Verify ROI polygons are valid (not self-intersecting)
- Check frame_dimensions are set in processor
- Ensure ROI is saved successfully

**Alert not triggering:**
- Check QUEUE_ALERT_THRESHOLD (default: 2)
- Verify QUEUE_DWELL_TIME_SEC (default: 3 seconds)
- Ensure people are detected in ROIs

## Server IP Configuration

The frontend automatically adapts to your server IP:
```javascript
const socket = io(`http://${window.location.hostname}:5001`);
```

**Example:**
- Local: `http://localhost:5001`
- Server: `http://192.168.1.100:5001`
- Domain: `http://yourserver.com:5001`

No manual configuration needed! It uses the same hostname you access the dashboard from.

## Troubleshooting

### Canvas not showing:
```javascript
// Check browser console for errors
// Verify .roi-canvas style is set to display: block
```

### ROI not saving:
```bash
# Check backend logs
tail -f /path/to/logs

# Verify database connection
# Check roi_configs table
```

### Detection History not showing:
```bash
# Verify detections are being saved
ls -la static/detections/QueueMonitor_*

# Check detections table in database
SELECT * FROM detections WHERE app_name = 'QueueMonitor';
```

## Code References

**Key Files:**
- Frontend: `templates/dashboard.html` (lines 218-283, 429)
- Processor: `processors/queue_monitor_processor.py` (lines 59-76, 146-195)
- Backend API: `main_app.py` (lines 374-401)
- Database: `main_app.py` (lines 96-102)

## Summary

The Edit ROI feature provides a visual, interactive way to define monitoring zones:
1. ✅ Draw directly on live video feed
2. ✅ Two independent polygons (Main + Secondary)
3. ✅ Real-time visual feedback
4. ✅ Persistent storage in database
5. ✅ Automatic loading on startup
6. ✅ Live updates without restart
7. ✅ Works with any server IP

This enables precise queue monitoring tailored to your specific camera view and layout!

