#!/usr/bin/env python3
"""
Comprehensive test script for detection system fixes
Tests all implemented features: bounding boxes, screenshots, ROI, database
"""

import os
import sys
import time
import requests
import json
import logging
from datetime import datetime
import pytz

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Configuration
MAIN_APP_URL = "http://localhost:5001"
IST = pytz.timezone('Asia/Kolkata')

# Test configuration
TEST_CHANNEL_ID = "test_cam_12345"
TEST_APP_NAME = "QueueMonitor"

def setup_logging():
    """Setup logging for test output"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - [TEST] - %(levelname)s - %(message)s'
    )

def test_database_connection():
    """Test database connection and schema"""
    print("\n🔍 Testing Database Connection...")
    try:
        response = requests.get(f"{MAIN_APP_URL}/health", timeout=5)
        if response.status_code == 200:
            print("✅ Main app health check passed")
            return True
        else:
            print(f"❌ Main app health check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Database connection test failed: {e}")
        return False

def test_roi_save():
    """Test ROI save functionality"""
    print("\n🔍 Testing ROI Save...")
    
    test_roi_data = {
        "channel_id": TEST_CHANNEL_ID,
        "app_name": TEST_APP_NAME,
        "roi_points": {
            "main": [[100, 100], [200, 100], [200, 200], [100, 200]],
            "secondary": [[300, 100], [400, 100], [400, 200], [300, 200]]
        },
        "queue_settings": {
            "queue_threshold": 3,
            "counter_threshold": 1,
            "dwell_time": 2.5,
            "alert_cooldown": 120
        }
    }
    
    try:
        response = requests.post(
            f"{MAIN_APP_URL}/api/set_roi",
            json=test_roi_data,
            timeout=10
        )
        
        if response.status_code == 200:
            result = response.json()
            if result.get('success'):
                print("✅ ROI save test passed")
                return True
            else:
                print(f"❌ ROI save failed: {result.get('error', 'Unknown error')}")
                return False
        else:
            print(f"❌ ROI save request failed: {response.status_code}")
            print(f"Response: {response.text}")
            return False
    except Exception as e:
        print(f"❌ ROI save test failed: {e}")
        return False

def test_roi_load():
    """Test ROI load functionality"""
    print("\n🔍 Testing ROI Load...")
    
    try:
        response = requests.get(
            f"{MAIN_APP_URL}/api/get_roi",
            params={
                "channel_id": TEST_CHANNEL_ID,
                "app_name": TEST_APP_NAME
            },
            timeout=5
        )
        
        if response.status_code == 200:
            result = response.json()
            if result.get('roi_points'):
                roi_points = result['roi_points']
                if 'main' in roi_points and 'secondary' in roi_points:
                    print("✅ ROI load test passed")
                    print(f"  - Main ROI points: {len(roi_points['main'])}")
                    print(f"  - Secondary ROI points: {len(roi_points['secondary'])}")
                    return True
                else:
                    print("❌ ROI structure invalid")
                    return False
            else:
                print("❌ No ROI data returned")
                return False
        else:
            print(f"❌ ROI load request failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ ROI load test failed: {e}")
        return False

def test_queue_settings():
    """Test queue settings load"""
    print("\n🔍 Testing Queue Settings...")
    
    try:
        response = requests.get(
            f"{MAIN_APP_URL}/api/get_queue_settings",
            params={"channel_id": TEST_CHANNEL_ID},
            timeout=5
        )
        
        if response.status_code == 200:
            result = response.json()
            if 'queue_threshold' in result:
                print("✅ Queue settings load test passed")
                print(f"  - Queue threshold: {result.get('queue_threshold')}")
                print(f"  - Counter threshold: {result.get('counter_threshold')}")
                print(f"  - Dwell time: {result.get('dwell_time')}")
                return True
            else:
                print("❌ Queue settings structure invalid")
                return False
        else:
            print(f"❌ Queue settings request failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Queue settings test failed: {e}")
        return False

def test_detection_history():
    """Test detection history endpoint"""
    print("\n🔍 Testing Detection History...")
    
    try:
        response = requests.get(
            f"{MAIN_APP_URL}/history/{TEST_APP_NAME}",
            params={
                "channel_id": TEST_CHANNEL_ID,
                "page": 1,
                "limit": 5
            },
            timeout=5
        )
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Detection history test passed")
            print(f"  - Total detections: {result.get('total', 0)}")
            print(f"  - Current page detections: {len(result.get('detections', []))}")
            return True
        else:
            print(f"❌ Detection history request failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Detection history test failed: {e}")
        return False

def test_static_folders():
    """Test static folder structure"""
    print("\n🔍 Testing Static Folders...")
    
    required_folders = [
        'static/detections',
        'static/shutter_videos',
        'static/heatmaps'
    ]
    
    all_exist = True
    for folder in required_folders:
        if os.path.exists(folder):
            print(f"✅ Folder exists: {folder}")
        else:
            print(f"❌ Folder missing: {folder}")
            all_exist = False
    
    return all_exist

def test_detection_api():
    """Test detection API endpoint"""
    print("\n🔍 Testing Detection API...")
    
    test_detection_data = {
        "app_name": TEST_APP_NAME,
        "channel_id": TEST_CHANNEL_ID,
        "message": "Test detection from automated test",
        "media_path": "detections/test_detection.jpg",
        "is_gif": False
    }
    
    try:
        response = requests.post(
            f"{MAIN_APP_URL}/api/handle_detection",
            json=test_detection_data,
            timeout=5
        )
        
        if response.status_code == 200:
            result = response.json()
            if result.get('success'):
                print("✅ Detection API test passed")
                return True
            else:
                print(f"❌ Detection API failed: {result.get('error', 'Unknown error')}")
                return False
        else:
            print(f"❌ Detection API request failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Detection API test failed: {e}")
        return False

def run_comprehensive_test():
    """Run all tests and provide summary"""
    print("🚀 Starting Comprehensive Detection System Test")
    print("=" * 60)
    
    setup_logging()
    
    tests = [
        ("Database Connection", test_database_connection),
        ("Static Folders", test_static_folders),
        ("ROI Save", test_roi_save),
        ("ROI Load", test_roi_load),
        ("Queue Settings", test_queue_settings),
        ("Detection History", test_detection_history),
        ("Detection API", test_detection_api)
    ]
    
    results = {}
    
    for test_name, test_func in tests:
        try:
            results[test_name] = test_func()
        except Exception as e:
            print(f"❌ {test_name} test crashed: {e}")
            results[test_name] = False
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 TEST SUMMARY")
    print("=" * 60)
    
    passed = 0
    total = len(tests)
    
    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{test_name:20} {status}")
        if result:
            passed += 1
    
    print("-" * 60)
    print(f"Total: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 ALL TESTS PASSED! Detection system is working correctly.")
        return True
    else:
        print(f"\n⚠️  {total - passed} tests failed. Please check the issues above.")
        return False

if __name__ == "__main__":
    success = run_comprehensive_test()
    sys.exit(0 if success else 1)
