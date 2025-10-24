#!/usr/bin/env python3
"""
Frontend Testing Script for Sakshi.AI Dashboard
Tests Socket.IO events and REST API endpoints
"""

import requests
import time
from socketio import Client
import sys

# Configuration
BASE_URL = "http://localhost:5000"
TEST_CHANNEL_ID = "test_channel_001"

print("=" * 60)
print("Sakshi.AI Frontend Test Suite")
print("=" * 60)

# Test 1: Health Check
print("\n[TEST 1] Health Check...")
try:
    response = requests.get(f"{BASE_URL}/health", timeout=5)
    if response.status_code == 200:
        print("✅ Health check passed:", response.json())
    else:
        print("❌ Health check failed with status:", response.status_code)
except Exception as e:
    print("❌ Health check error:", str(e))
    print("⚠️  Make sure the Flask app is running on port 5000")
    sys.exit(1)

# Test 2: Dashboard Page
print("\n[TEST 2] Dashboard Page...")
try:
    response = requests.get(f"{BASE_URL}/dashboard", timeout=5)
    if response.status_code == 200 and "Sakshi.AI Dashboard" in response.text:
        print("✅ Dashboard page loads successfully")
    else:
        print("❌ Dashboard page failed")
except Exception as e:
    print("❌ Dashboard error:", str(e))

# Test 3: Socket.IO Connection
print("\n[TEST 3] Socket.IO Connection...")
sio = Client()
connection_success = False
events_received = []

@sio.on('connect')
def on_connect():
    global connection_success
    connection_success = True
    print("✅ Socket.IO connected successfully")

@sio.on('disconnect')
def on_disconnect():
    print("⚠️  Socket.IO disconnected")

@sio.on('connect_error')
def on_connect_error(data):
    print("❌ Socket.IO connection error:", data)

@sio.on('count_update')
def on_count_update(data):
    events_received.append(('count_update', data))
    print(f"📊 Received count_update: {data}")

@sio.on('queue_update')
def on_queue_update(data):
    events_received.append(('queue_update', data))
    print(f"📊 Received queue_update: {data}")

@sio.on('shutter_update')
def on_shutter_update(data):
    events_received.append(('shutter_update', data))
    print(f"📊 Received shutter_update: {data}")

@sio.on('new_detection')
def on_new_detection(data):
    events_received.append(('new_detection', data))
    print(f"📊 Received new_detection: {data}")

@sio.on('security_violation')
def on_security_violation(data):
    events_received.append(('security_violation', data))
    print(f"📊 Received security_violation: {data}")

try:
    sio.connect(BASE_URL)
    time.sleep(2)  # Wait for potential events
    
    if connection_success:
        print("✅ Socket.IO setup complete")
    else:
        print("❌ Socket.IO connection failed")
        
except Exception as e:
    print("❌ Socket.IO error:", str(e))
    sio.disconnect()

# Test 4: API Endpoints
print("\n[TEST 4] REST API Endpoints...")

endpoints_to_test = [
    ("/", "Landing Page"),
    ("/dashboard", "Dashboard"),
]

for endpoint, name in endpoints_to_test:
    try:
        response = requests.get(f"{BASE_URL}{endpoint}", timeout=5)
        if response.status_code == 200:
            print(f"✅ {name}: OK")
        else:
            print(f"❌ {name}: Status {response.status_code}")
    except Exception as e:
        print(f"❌ {name}: {str(e)}")

# Test 5: Check RTSP Links Configuration
print("\n[TEST 5] Configuration Files...")
import os

config_files = [
    "config/rtsp_links.txt",
    "requirements.txt",
    "docker-compose.yml"
]

for config_file in config_files:
    if os.path.exists(config_file):
        print(f"✅ {config_file}: exists")
    else:
        print(f"❌ {config_file}: missing")

# Test 6: Database Check (if accessible)
print("\n[TEST 6] Database Check...")
try:
    from sqlalchemy import create_engine, text
    DATABASE_URL = os.environ.get('DATABASE_URL', "postgresql+psycopg2://postgres:Tneural01@localhost:5432/sakshi")
    engine = create_engine(DATABASE_URL, pool_pre_ping=True)
    
    with engine.connect() as conn:
        # Check detections table
        result = conn.execute(text("SELECT COUNT(*) FROM detections"))
        count = result.scalar()
        print(f"✅ Detections table: {count} records")
        
        # Check shutter_logs table
        result = conn.execute(text("SELECT COUNT(*) FROM shutter_logs"))
        count = result.scalar()
        print(f"✅ Shutter logs table: {count} records")
        
        # Check security_violations table
        result = conn.execute(text("SELECT COUNT(*) FROM security_violations"))
        count = result.scalar()
        print(f"✅ Security violations table: {count} records")
        
except Exception as e:
    print(f"⚠️  Database check skipped: {str(e)}")

# Cleanup
try:
    sio.disconnect()
except:
    pass

# Summary
print("\n" + "=" * 60)
print("Test Summary")
print("=" * 60)
print(f"Socket.IO Events Received: {len(events_received)}")
if events_received:
    for event_type, data in events_received:
        print(f"  - {event_type}: {data}")
else:
    print("⚠️  No real-time events received during test")
    print("   This is normal if no processors are actively running")

print("\n" + "=" * 60)
print("Frontend Testing Complete!")
print("=" * 60)
print("\nNext Steps:")
print("1. Open browser and navigate to http://localhost:5000/dashboard")
print("2. Open Developer Tools (F12) and check Console tab")
print("3. Look for '✅ Socket.IO connected successfully'")
print("4. Verify real-time data updates are working")
print("=" * 60)

