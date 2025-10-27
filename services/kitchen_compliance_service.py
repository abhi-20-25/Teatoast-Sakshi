#!/usr/bin/env python3
"""
Kitchen Compliance Processor Microservice
Monitors kitchen safety and compliance
"""

import os
import sys
import time
import logging
import hashlib
import requests

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from processors.kitchen_compliance_monitor import KitchenComplianceProcessor, KitchenViolation
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Configuration
DATABASE_URL = os.environ.get('DATABASE_URL', 'postgresql+psycopg2://postgres:Tneural01@postgres:5432/sakshi')
MAIN_APP_URL = os.environ.get('MAIN_APP_URL', 'http://main-app:5001')
TELEGRAM_BOT_TOKEN = os.environ.get('TELEGRAM_BOT_TOKEN', '')
TELEGRAM_CHAT_ID = os.environ.get('TELEGRAM_CHAT_ID', '')
CONFIG_FOLDER = '/app/config'
RTSP_LINKS_FILE = os.path.join(CONFIG_FOLDER, 'rtsp_links.txt')

# Logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - [KITCHEN_COMPLIANCE] - %(levelname)s - %(message)s'
)

def get_stable_channel_id(link):
    """Generate stable channel ID from RTSP link"""
    return f"cam_{hashlib.md5(link.encode()).hexdigest()[:10]}"

def send_telegram_notification(message):
    """Send Telegram notification"""
    if not TELEGRAM_BOT_TOKEN or "YOUR_TELEGRAM" in TELEGRAM_BOT_TOKEN:
        return
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {'chat_id': TELEGRAM_CHAT_ID, 'text': message, 'parse_mode': 'Markdown'}
    try:
        requests.post(url, json=payload, timeout=5)
    except Exception as e:
        logging.error(f"Error sending Telegram notification: {e}")

def handle_detection(app_name, channel_id, frames, message, is_gif=False):
    """Handle detection and save to database with image storage"""
    from datetime import datetime
    import pytz
    import cv2
    import imageio
    
    IST = pytz.timezone('Asia/Kolkata')
    timestamp = datetime.now(IST)
    ts_string = timestamp.strftime("%Y%m%d_%H%M%S")
    filename = f"{app_name}_{channel_id}_{ts_string}.{'gif' if is_gif else 'jpg'}"
    media_path = os.path.join('detections', filename)
    full_path = os.path.join('/app/static', media_path)
    
    try:
        os.makedirs(os.path.dirname(full_path), exist_ok=True)
        if is_gif and isinstance(frames, list) and len(frames) > 1:
            rgb_frames = [cv2.cvtColor(f, cv2.COLOR_BGR2RGB) for f in frames]
            imageio.mimsave(full_path, rgb_frames, fps=10)
        else:
            frame_to_save = frames[0] if isinstance(frames, list) else frames
            cv2.imwrite(full_path, frame_to_save)
        logging.info(f"Saved kitchen detection: {filename}")
    except Exception as e:
        logging.error(f"Failed to save media file '{full_path}': {e}")
        return None

    # Save to database
    try:
        with SessionLocal() as db:
            from main_app import Detection
            db.add(Detection(
                app_name=app_name,
                channel_id=channel_id,
                timestamp=timestamp,
                message=message,
                media_path=media_path
            ))
            db.commit()
    except Exception as e:
        logging.error(f"Failed to save detection to DB: {e}")

    # Notify main app
    try:
        media_url = f"/static/{media_path}".replace('\\', '/')
        requests.post(
            f"{MAIN_APP_URL}/api/detection_event",
            json={
                'app_name': app_name,
                'channel_id': channel_id,
                'timestamp': timestamp.strftime("%Y-%m-%d %H:%M:%S"),
                'message': message,
                'media_url': media_url
            },
            timeout=5
        )
    except Exception as e:
        logging.warning(f"Failed to notify main app: {e}")

    return media_path

# Mock SocketIO
class MockSocketIO:
    def emit(self, event, data):
        try:
            requests.post(
                f"{MAIN_APP_URL}/api/socketio_event",
                json={'event': event, 'data': data},
                timeout=2
            )
        except Exception as e:
            logging.debug(f"Failed to emit event: {e}")

def main():
    """Main service function"""
    logging.info("🚀 Starting Kitchen Compliance Processor Microservice")
    
    # Initialize database
    try:
        engine = create_engine(DATABASE_URL, pool_pre_ping=True)
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
        KitchenComplianceProcessor.initialize_tables(engine)
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

    # Parse RTSP links and start processors
    if not os.path.exists(RTSP_LINKS_FILE):
        logging.error(f"Configuration file not found: {RTSP_LINKS_FILE}")
        sys.exit(1)

    processors = []
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
                
                if 'KitchenCompliance' in app_names:
                    channel_id = get_stable_channel_id(link)
                    processor = KitchenComplianceProcessor(
                        link, channel_id, channel_name,
                        SessionLocal, socketio,
                        send_telegram_notification, handle_detection
                    )
                    processor.start()
                    processors.append(processor)
                    logging.info(f"Started kitchen compliance for {channel_name}")

    if not processors:
        logging.warning("No kitchen compliance processors configured")
        sys.exit(0)
    
    # Start video server
    from video_server_mixin import start_video_server_for_processors
    start_video_server_for_processors(processors, 5015)
    
    # Keep service running
    try:
        while True:
            time.sleep(10)
            for p in processors:
                if not p.is_alive():
                    logging.error(f"Processor {p.name} died")
    except KeyboardInterrupt:
        logging.info("Shutting down...")
        for p in processors:
            if hasattr(p, 'stop'):
                p.stop()
        sys.exit(0)

if __name__ == "__main__":
    main()

