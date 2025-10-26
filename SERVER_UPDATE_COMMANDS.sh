#!/bin/bash
# SERVER UPDATE SCRIPT - Excel Time Parsing Fix
# This script updates the server with the latest Excel parsing improvements

set -e  # Exit on error

echo "=========================================="
echo "  SAKSHI AI - SERVER UPDATE SCRIPT"
echo "  Excel Time Parsing Fix for Occupancy Monitor"
echo "=========================================="
echo ""

# Step 1: Navigate to project directory
echo "Step 1: Navigating to project directory..."
cd /home/ubuntu/Sakshi-Teatoast-Fresh || cd /path/to/Sakshi-21-OCT
echo "✓ Current directory: $(pwd)"
echo ""

# Step 2: Pull latest changes
echo "Step 2: Fetching latest changes from GitHub..."
git fetch origin
echo "✓ Fetched latest changes"
echo ""

echo "Step 3: Checking out fix branch..."
git checkout fix/openpyxl-postgresql-detection-images
echo "✓ Switched to fix branch"
echo ""

echo "Step 4: Pulling latest code..."
git pull origin fix/openpyxl-postgresql-detection-images
echo "✓ Code updated"
echo ""

# Step 3: Stop services
echo "Step 5: Stopping Docker services..."
docker-compose down
echo "✓ Services stopped"
echo ""

# Step 4: Rebuild occupancy monitor
echo "Step 6: Rebuilding Occupancy Monitor container..."
docker-compose build --no-cache occupancy-monitor-processor
echo "✓ Container rebuilt"
echo ""

# Step 5: Start services
echo "Step 7: Starting all services..."
docker-compose up -d
echo "✓ Services started"
echo ""

# Step 6: Wait for services to initialize
echo "Step 8: Waiting for services to initialize (10 seconds)..."
sleep 10
echo "✓ Initialization complete"
echo ""

# Step 7: Check service status
echo "Step 9: Checking service status..."
docker-compose ps
echo ""

# Step 8: Verify openpyxl
echo "Step 10: Verifying openpyxl installation..."
docker exec sakshi-occupancy-monitor pip list | grep openpyxl
echo "✓ openpyxl verified"
echo ""

# Step 9: Show logs
echo "=========================================="
echo "  UPDATE COMPLETE!"
echo "=========================================="
echo ""
echo "Showing recent logs (press Ctrl+C to exit)..."
echo ""
docker-compose logs --tail=50 occupancy-monitor-processor

echo ""
echo "To continue monitoring logs:"
echo "  docker-compose logs -f occupancy-monitor-processor"
echo ""
echo "To test Excel upload:"
echo "  1. Open http://your-server-ip:5001/dashboard"
echo "  2. Navigate to Occupancy Monitor"
echo "  3. Upload .xlsx schedule file"
echo "  4. Should see: 'X time slots configured' (not 0)"
echo ""

