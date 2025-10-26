#!/bin/bash
# ════════════════════════════════════════════════════════════════
# Sakshi Occupancy Monitor - Clean Server Deployment
# Branch: feature/occupancy-monitor-production
# ════════════════════════════════════════════════════════════════

set -e  # Exit on error

echo "╔════════════════════════════════════════════════════════════════╗"
echo "║   🚀 Deploying Occupancy Monitor (Clean Install)             ║"
echo "╚════════════════════════════════════════════════════════════════╝"
echo ""

# Navigate to project
cd /home/ubuntu/Sakshi-Teatoast || { echo "❌ Directory not found"; exit 1; }
echo "✅ Project directory: $(pwd)"
echo ""

# Fetch latest from GitHub
echo "📥 Fetching from GitHub..."
git fetch origin
echo "✅ Fetched"
echo ""

# Switch to new branch (clean checkout)
echo "🔄 Switching to feature/occupancy-monitor-production branch..."
git checkout feature/occupancy-monitor-production
echo "✅ On correct branch"
echo ""

# Pull latest (should be clean now)
echo "📥 Pulling latest code..."
git pull origin feature/occupancy-monitor-production
echo "✅ Code updated"
echo ""

# Verify files exist
echo "🔍 Verifying Occupancy Monitor files..."
if [ -f "processors/occupancy_monitor_processor.py" ]; then
    echo "  ✓ processors/occupancy_monitor_processor.py"
else
    echo "  ❌ Missing processor file"
fi

if [ -f "services/occupancy_monitor_service.py" ]; then
    echo "  ✓ services/occupancy_monitor_service.py"
else
    echo "  ❌ Missing service file"
fi

if [ -f "docker/Dockerfile.occupancy_monitor" ]; then
    echo "  ✓ docker/Dockerfile.occupancy_monitor"
else
    echo "  ❌ Missing Dockerfile"
fi
echo ""

# Stop all containers
echo "🛑 Stopping all containers..."
docker-compose down --remove-orphans
echo "✅ Containers stopped"
echo ""

# Build occupancy monitor
echo "🔨 Building Occupancy Monitor container..."
docker-compose build occupancy-monitor-processor
echo "✅ Container built"
echo ""

# Start all services
echo "🚀 Starting all services..."
docker-compose up -d --remove-orphans
echo "✅ Services started"
echo ""

# Wait for initialization
echo "⏳ Waiting for services to initialize (30 seconds)..."
sleep 30
echo ""

# Show status
echo "════════════════════════════════════════════════════════════════"
echo "📊 Container Status"
echo "════════════════════════════════════════════════════════════════"
docker-compose ps
echo ""

# Check device
echo "════════════════════════════════════════════════════════════════"
echo "💻 Occupancy Monitor - Device Detection"
echo "════════════════════════════════════════════════════════════════"
docker-compose logs occupancy-monitor-processor | grep "Using device" || echo "Still initializing..."
echo ""

# Check health
echo "════════════════════════════════════════════════════════════════"
echo "🏥 Health Check"
echo "════════════════════════════════════════════════════════════════"
curl -s http://localhost:5017/health | python3 -m json.tool 2>/dev/null || echo "Service starting..."
echo ""

# Recent logs
echo "════════════════════════════════════════════════════════════════"
echo "📝 Recent Logs (Last 15 lines)"
echo "════════════════════════════════════════════════════════════════"
docker-compose logs --tail=15 occupancy-monitor-processor
echo ""

# Final message
echo "════════════════════════════════════════════════════════════════"
echo "✅ DEPLOYMENT COMPLETE!"
echo "════════════════════════════════════════════════════════════════"
SERVER_IP=$(hostname -I | awk '{print $1}')
echo ""
echo "Access Points:"
echo "  Dashboard: http://$SERVER_IP:5001/dashboard"
echo "  API: http://localhost:5017/health"
echo ""
echo "Next Steps:"
echo "  1. Open dashboard in browser"
echo "  2. Find 'Occupancy Monitor' section"
echo "  3. Upload schedule (.xlsx)"
echo "  4. Watch detection working on CPU!"
echo ""
echo "View logs: docker-compose logs -f occupancy-monitor-processor"
echo "════════════════════════════════════════════════════════════════"

