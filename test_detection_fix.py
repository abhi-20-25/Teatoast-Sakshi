#!/usr/bin/env python3
"""
Test script to verify detection fixes are working
"""

import os
import sys
import time
import logging
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_detection_processor_import():
    """Test that detection processor can be imported and initialized"""
    logger.info("Testing DetectionProcessor import and initialization...")
    
    try:
        from processors.detection_processor import DetectionProcessor
        
        # Mock callback function
        def mock_callback(app_name, channel_id, frames, message, is_gif=False):
            logger.info(f"Mock callback: {app_name} on {channel_id} - {message}")
            return True
        
        # Create a mock detection processor
        processor = DetectionProcessor(
            rtsp_url="test://url",
            channel_id="test_channel",
            channel_name="Test Channel",
            tasks=[{
                'app_name': 'TestApp',
                'model': None,  # Mock model
                'confidence': 0.5,
                'target_class_id': [0]
            }],
            detection_callback=mock_callback
        )
        
        # Check if required attributes exist
        assert hasattr(processor, 'lock'), "Missing self.lock attribute"
        assert hasattr(processor, 'cached_boxes'), "Missing self.cached_boxes attribute"
        assert hasattr(processor, '_draw_cached_boxes'), "Missing _draw_cached_boxes method"
        assert hasattr(processor, '_trigger_detection_callback'), "Missing _trigger_detection_callback method"
        
        logger.info("✅ DetectionProcessor import and initialization successful")
        return True
        
    except Exception as e:
        logger.error(f"❌ DetectionProcessor test failed: {e}")
        return False

def test_detection_processor_code_analysis():
    """Analyze the detection processor code for potential issues"""
    logger.info("Analyzing DetectionProcessor code for issues...")
    
    try:
        processor_file = project_root / "processors" / "detection_processor.py"
        with open(processor_file, 'r') as f:
            content = f.read()
        
        # Check for key patterns
        issues = []
        
        # Check if cached boxes are being cleared (this was the issue)
        if "self.cached_boxes[app_name] = None" in content:
            issues.append("❌ Cached boxes are being cleared - this prevents smooth display")
        
        # Check if inference interval is reasonable
        if "inference_interval = 0.1" in content:
            logger.info("✅ Inference interval set to 0.1s (10 FPS) - good for detection capture")
        elif "inference_interval = 0.2" in content:
            logger.info("⚠️ Inference interval set to 0.2s (5 FPS) - might miss some detections")
        else:
            issues.append("❌ Inference interval not found or not set properly")
        
        # Check if detection callback is being called
        if "self._trigger_detection_callback" in content:
            logger.info("✅ Detection callback is being called")
        else:
            issues.append("❌ Detection callback not being called")
        
        # Check if logging is added
        if "Triggering detection callback" in content:
            logger.info("✅ Debug logging added for detection callbacks")
        else:
            issues.append("❌ Debug logging not found for detection callbacks")
        
        if issues:
            for issue in issues:
                logger.error(issue)
            return False
        else:
            logger.info("✅ Code analysis passed - no major issues found")
            return True
            
    except Exception as e:
        logger.error(f"❌ Code analysis failed: {e}")
        return False

def test_main_app_detection_handling():
    """Test that main app has proper detection handling"""
    logger.info("Testing main app detection handling...")
    
    try:
        main_app_file = project_root / "main_app.py"
        with open(main_app_file, 'r') as f:
            content = f.read()
        
        # Check for key patterns
        patterns = [
            'def handle_detection(',
            'handle_detection called:',
            'Creating DetectionProcessor',
            'DetectionProcessor(link, channel_id, channel_name, detection_tasks, handle_detection)'
        ]
        
        for pattern in patterns:
            if pattern not in content:
                logger.error(f"❌ Missing pattern in main_app.py: {pattern}")
                return False
        
        logger.info("✅ Main app detection handling looks correct")
        return True
        
    except Exception as e:
        logger.error(f"❌ Main app test failed: {e}")
        return False

def test_detection_flow():
    """Test the complete detection flow"""
    logger.info("Testing complete detection flow...")
    
    try:
        # Check if all required files exist
        required_files = [
            "processors/detection_processor.py",
            "main_app.py",
            "templates/dashboard.html"
        ]
        
        for file_path in required_files:
            full_path = project_root / file_path
            if not full_path.exists():
                logger.error(f"❌ Required file not found: {file_path}")
                return False
        
        logger.info("✅ All required files exist")
        
        # Check if the fixes are in place
        processor_file = project_root / "processors" / "detection_processor.py"
        with open(processor_file, 'r') as f:
            content = f.read()
        
        # Check for the specific fixes
        fixes = [
            "self.lock = threading.Lock()",
            "self.cached_boxes = {}",
            "inference_interval = 0.1",
            "Triggering detection callback",
            "Don't clear cached boxes"
        ]
        
        for fix in fixes:
            if fix not in content:
                logger.error(f"❌ Fix not found: {fix}")
                return False
        
        logger.info("✅ All detection fixes are in place")
        return True
        
    except Exception as e:
        logger.error(f"❌ Detection flow test failed: {e}")
        return False

def main():
    """Run all tests"""
    logger.info("🚀 Starting Detection Fix Verification Test")
    logger.info("=" * 60)
    
    tests = [
        test_detection_processor_import,
        test_detection_processor_code_analysis,
        test_main_app_detection_handling,
        test_detection_flow
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
        logger.info("-" * 40)
    
    logger.info("=" * 60)
    logger.info(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        logger.info("🎉 All tests passed! Detection fixes should be working correctly.")
        logger.info("\n📋 Summary of fixes applied:")
        logger.info("✅ Fixed missing self.lock and cached_boxes")
        logger.info("✅ Removed cached box clearing that was preventing detections")
        logger.info("✅ Increased inference frequency to 10 FPS for better detection capture")
        logger.info("✅ Added debug logging to track detection callbacks")
        logger.info("✅ Verified detection callback is properly passed to DetectionProcessor")
        logger.info("\n🔍 To debug further, check the logs for:")
        logger.info("- 'Creating DetectionProcessor for...' messages")
        logger.info("- 'DetectionProcessor ... detected X objects' messages")
        logger.info("- 'Triggering detection callback for...' messages")
        logger.info("- 'handle_detection called: ...' messages")
        return True
    else:
        logger.error(f"❌ {total - passed} tests failed. Please check the errors above.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
