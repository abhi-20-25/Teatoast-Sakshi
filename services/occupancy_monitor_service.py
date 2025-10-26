#!/usr/bin/env python3
"""
Live Occupancy Monitor Microservice
Follows the same pattern as people_counter_service.py
"""

import os
import sys
import time
import logging
import hashlib
import requests

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from processors.occupancy_monitor_processor import OccupancyMonitorProcessor, OccupancyLog, OccupancySchedule
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import torch
from ultralytics import YOLO
from flask import Flask, Response, jsonify, request
from werkzeug.utils import secure_filename
import openpyxl
import csv
from datetime import datetime as dt, time as dt_time

# Configuration
DATABASE_URL = os.environ.get('DATABASE_URL', 'postgresql+psycopg2://postgres:Tneural01@postgres:5432/sakshi')
MAIN_APP_URL = os.environ.get('MAIN_APP_URL', 'http://localhost:5001')
TELEGRAM_BOT_TOKEN = os.environ.get('TELEGRAM_BOT_TOKEN', '')
TELEGRAM_CHAT_ID = os.environ.get('TELEGRAM_CHAT_ID', '')
CONFIG_FOLDER = '/app/config'
MODELS_FOLDER = '/app/models'
RTSP_LINKS_FILE = os.path.join(CONFIG_FOLDER, 'rtsp_links.txt')
MODEL_PATH = os.path.join(MODELS_FOLDER, 'yolov8n.pt')
UPLOAD_FOLDER = '/tmp'

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - [OCCUPANCY_MONITOR] - %(levelname)s - %(message)s'
)

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

processors = []

def get_stable_channel_id(link):
    """Generate stable channel ID from RTSP link"""
    return f"cam_{hashlib.md5(link.encode()).hexdigest()[:10]}"

def normalize_time_slot(time_value):
    """
    Normalize various time formats to H:00 format (without leading zeros)
    Handles: datetime objects, time objects, strings like "9:00", "09:00", "9:00:00", etc.
    Returns: "9:00", "14:00", etc.
    """
    if time_value is None:
        return None
    
    try:
        # If it's a datetime object
        if isinstance(time_value, dt):
            return f"{time_value.hour}:00"
        
        # If it's a time object
        if isinstance(time_value, dt_time):
            return f"{time_value.hour}:00"
        
        # If it's a string, parse it
        time_str = str(time_value).strip()
        
        # Remove seconds if present (e.g., "09:00:00" -> "09:00")
        if time_str.count(':') == 2:
            time_str = ':'.join(time_str.split(':')[:2])
        
        # Parse the hour part
        if ':' in time_str:
            hour_str = time_str.split(':')[0]
            hour = int(hour_str)
            
            # Return in H:00 format (no leading zero for single digit)
            return f"{hour}:00"
        
        # If it's just a number (hour only)
        hour = int(time_str)
        return f"{hour}:00"
        
    except (ValueError, AttributeError) as e:
        logging.warning(f"Could not parse time value '{time_value}': {e}")
        return None

def parse_csv_schedule(filepath):
    """Parse CSV file and return schedule data"""
    schedule_data = {}
    parsed_count = 0
    
    with open(filepath, 'r', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        
        for row in reader:
            # Get time slot from first column (usually 'Time')
            time_key = None
            for key in row.keys():
                if key and key.lower().strip() in ['time', 'hour', 'slot']:
                    time_key = key
                    break
            
            if not time_key or not row[time_key]:
                continue
            
            time_slot = normalize_time_slot(row[time_key])
            if not time_slot:
                continue
            
            schedule_data[time_slot] = {}
            
            # Parse day columns
            for day_name, value in row.items():
                if day_name == time_key or not day_name:
                    continue
                
                if value and value.strip():
                    try:
                        schedule_data[time_slot][day_name] = int(value)
                        parsed_count += 1
                    except (ValueError, TypeError) as e:
                        logging.warning(f"Could not parse count for {day_name} at {time_slot}: {e}")
    
    logging.info(f"Parsed {len(schedule_data)} time slots with {parsed_count} entries from CSV")
    return schedule_data, parsed_count

def parse_excel_schedule(filepath):
    """Parse Excel file and return schedule data"""
    schedule_data = {}
    parsed_count = 0
    
    wb = openpyxl.load_workbook(filepath)
    sheet = wb.active
    headers = [cell.value for cell in sheet[1]]
    
    for row in sheet.iter_rows(min_row=2, values_only=True):
        # Normalize time slot to H:00 format
        time_slot = normalize_time_slot(row[0])
        if not time_slot:
            continue
        
        schedule_data[time_slot] = {}
        for col_idx, day_name in enumerate(headers[1:], start=1):
            if col_idx < len(row) and row[col_idx] is not None:
                try:
                    schedule_data[time_slot][day_name] = int(row[col_idx])
                    parsed_count += 1
                except (ValueError, TypeError) as e:
                    logging.warning(f"Could not parse count for {day_name} at {time_slot}: {e}")
    
    logging.info(f"Parsed {len(schedule_data)} time slots with {parsed_count} entries from Excel")
    return schedule_data, parsed_count

def load_model(model_path):
    """Load YOLO model"""
    device = 'cuda' if torch.cuda.is_available() else 'cpu'
    if not os.path.exists(model_path):
        logging.error(f"Model file not found: {model_path}")
        return None
    try:
        model = YOLO(model_path)
        model.to(device)
        logging.info(f"Loaded model on '{device}'")
        return model
    except Exception as e:
        logging.error(f"Failed to load model: {e}")
        return None

class MockSocketIO:
    """Mock SocketIO for standalone operation"""
    def emit(self, event, data):
        try:
            requests.post(
                f"{MAIN_APP_URL}/api/socketio_event",
                json={'event': event, 'data': data},
                timeout=2
            )
        except Exception as e:
            logging.debug(f"Failed to emit event: {e}")

def send_telegram_notification(message):
    """Send notification to Telegram"""
    if not TELEGRAM_BOT_TOKEN or "YOUR_TELEGRAM" in TELEGRAM_BOT_TOKEN:
        logging.debug("Telegram not configured")
        return
    
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
        payload = {'chat_id': TELEGRAM_CHAT_ID, 'text': message, 'parse_mode': 'Markdown'}
        requests.post(url, json=payload, timeout=5)
        logging.info("Telegram notification sent")
    except Exception as e:
        logging.error(f"Error sending Telegram notification: {e}")

# Flask Routes
@app.route('/health')
def health():
    """Health check endpoint"""
    alive_count = sum(1 for p in processors if p.is_alive())
    return jsonify({
        "status": "healthy",
        "alive_count": alive_count,
        "total_count": len(processors)
    })

@app.route('/video_feed/<channel_id>')
def video_feed(channel_id):
    """Stream video feed for a channel"""
    processor = next((p for p in processors if p.channel_id == channel_id), None)
    
    if not processor:
        return ("Channel not found", 404)
    
    def generate():
        while processor.is_running:
            frame_bytes = processor.get_frame()
            if frame_bytes:
                yield (b'--frame\r\n'
                       b'Content-Type: image/jpeg\r\n'
                       b'Cache-Control: no-store, no-cache, must-revalidate, max-age=0\r\n'
                       b'\r\n' + frame_bytes + b'\r\n')
            time.sleep(0.01)  # 100 FPS for smooth real-time streaming
    
    return Response(generate(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/api/upload_schedule/<channel_id>', methods=['POST'])
def upload_schedule(channel_id):
    """Upload CSV or Excel schedule for a specific channel"""
    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400
    
    file = request.files['file']
    
    # Accept both .xlsx and .csv files
    is_excel = file.filename.endswith('.xlsx')
    is_csv = file.filename.endswith('.csv')
    
    if file.filename == '' or not (is_excel or is_csv):
        return jsonify({'error': 'Invalid file. Please upload .xlsx or .csv file'}), 400
    
    processor = next((p for p in processors if p.channel_id == channel_id), None)
    if not processor:
        return jsonify({'error': 'Channel not found'}), 404
    
    try:
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        
        # Parse based on file type
        if is_csv:
            schedule_data, parsed_count = parse_csv_schedule(filepath)
            file_type = "CSV"
        else:
            schedule_data, parsed_count = parse_excel_schedule(filepath)
            file_type = "Excel"
        
        # Update processor schedule
        success = processor.update_schedule(schedule_data)
        os.remove(filepath)
        
        if success:
            return jsonify({
                'success': True, 
                'message': f'Schedule uploaded for {processor.channel_name}! {len(schedule_data)} time slots configured from {file_type} file.'
            })
        else:
            return jsonify({'error': 'Failed to update schedule'}), 500
            
    except Exception as e:
        logging.error(f"Error uploading schedule: {e}")
        if os.path.exists(filepath):
            os.remove(filepath)
        return jsonify({'error': str(e)}), 500

@app.route('/api/reload_schedule/<channel_id>', methods=['POST'])
def reload_schedule(channel_id):
    """Reload schedule from database for a specific channel"""
    processor = next((p for p in processors if p.channel_id == channel_id), None)
    
    if not processor:
        return jsonify({'error': 'Channel not found'}), 404
    
    processor._load_schedule_from_db()
    return jsonify({'success': True, 'message': 'Schedule reloaded'})

@app.route('/api/occupancy_stats/<channel_id>')
def occupancy_stats(channel_id):
    """Get occupancy statistics for a channel"""
    processor = next((p for p in processors if p.channel_id == channel_id), None)
    
    if not processor:
        return jsonify({'error': 'Channel not found'}), 404
    
    return jsonify({
        'channel_id': processor.channel_id,
        'channel_name': processor.channel_name,
        'live_count': processor.live_count,
        'required_count': processor.required_count,
        'current_time_slot': processor.current_time_slot,
        'schedule_loaded': len(processor.schedule) > 0
    })

def main():
    global processors
    
    logging.info("🚀 Starting Live Occupancy Monitor Microservice")
    
    # Initialize database
    try:
        engine = create_engine(DATABASE_URL, pool_pre_ping=True)
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
        OccupancyMonitorProcessor.initialize_tables(engine)
        logging.info("✅ Database connection established")
    except Exception as e:
        logging.error(f"❌ Database initialization failed: {e}")
        sys.exit(1)
    
    # Wait for main app
    logging.info("Waiting for main app...")
    for _ in range(30):
        try:
            requests.get(f"{MAIN_APP_URL}/health", timeout=2)
            break
        except:
            time.sleep(2)
    
    # Load model
    model = load_model(MODEL_PATH)
    if not model:
        logging.error("Failed to load model")
        sys.exit(1)
    
    # Parse RTSP links and start processors
    if not os.path.exists(RTSP_LINKS_FILE):
        logging.error(f"Configuration file not found: {RTSP_LINKS_FILE}")
        sys.exit(1)
    
    socketio = MockSocketIO()
    
    with open(RTSP_LINKS_FILE, 'r') as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            
            parts = [p.strip() for p in line.split(',')]
            if len(parts) >= 3:
                link, channel_name = parts[0], parts[1]
                app_names = set(parts[2:])
                
                # Check if OccupancyMonitor is enabled for this channel
                if 'OccupancyMonitor' in app_names:
                    channel_id = get_stable_channel_id(link)
                    processor = OccupancyMonitorProcessor(
                        link, channel_id, channel_name,
                        model, socketio, SessionLocal, send_telegram_notification
                    )
                    processor.start()
                    processors.append(processor)
                    logging.info(f"Started occupancy monitor for {channel_name}")
    
    if not processors:
        logging.warning("No occupancy monitor processors configured")
        logging.info("Add 'OccupancyMonitor' to rtsp_links.txt to enable")
        sys.exit(0)
    
    # Start Flask server
    logging.info("Starting Flask server on port 5017...")
    app.run(host='0.0.0.0', port=5017, threaded=True)

if __name__ == "__main__":
    main()

