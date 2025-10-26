#!/bin/bash
# ════════════════════════════════════════════════════════════════
# Sakshi Occupancy Monitor - Server Deployment Script
# ════════════════════════════════════════════════════════════════

echo "╔════════════════════════════════════════════════════════════════╗"
echo "║   🚀 Deploying Occupancy Monitor to Server (CPU Mode)        ║"
echo "╚════════════════════════════════════════════════════════════════╝"
echo ""

# Navigate to project directory
cd /home/ubuntu/Sakshi-Teatoast || { echo "❌ Project directory not found!"; exit 1; }
echo "✅ In project directory: $(pwd)"
echo ""

# Pull latest changes from git
echo "📥 Pulling latest changes from GitHub..."
git fetch origin
git pull origin modal-roi-queue-config-v3
echo "✅ Code updated from Git"
echo ""

# Stop all containers
echo "🛑 Stopping existing containers..."
docker-compose down
echo "✅ Containers stopped"
echo ""

# Remove orphaned containers
echo "🧹 Cleaning up orphaned containers..."
docker-compose down --remove-orphans
echo "✅ Cleanup complete"
echo ""

# Build occupancy monitor container
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

# Check status
echo "════════════════════════════════════════════════════════════════"
echo "📊 Deployment Status"
echo "════════════════════════════════════════════════════════════════"
docker-compose ps
echo ""

# Check occupancy monitor health
echo "════════════════════════════════════════════════════════════════"
echo "🔍 Occupancy Monitor Health Check"
echo "════════════════════════════════════════════════════════════════"
curl -s http://localhost:5017/health | python3 -m json.tool 2>/dev/null || echo "⚠️  Service still initializing..."
echo ""

# Check device (CPU/CUDA)
echo "════════════════════════════════════════════════════════════════"
echo "💻 Device Detection"
echo "════════════════════════════════════════════════════════════════"
docker-compose logs occupancy-monitor-processor | grep "Using device" || echo "Still starting..."
echo ""

# Show recent logs
echo "════════════════════════════════════════════════════════════════"
echo "📝 Recent Logs (Occupancy Monitor)"
echo "════════════════════════════════════════════════════════════════"
docker-compose logs --tail=20 occupancy-monitor-processor
echo ""

# Final status
echo "════════════════════════════════════════════════════════════════"
echo "✅ DEPLOYMENT COMPLETE!"
echo "════════════════════════════════════════════════════════════════"
echo ""
echo "Dashboard: http://$(hostname -I | awk '{print $1}'):5001/dashboard"
echo "Occupancy API: http://localhost:5017/health"
echo ""
echo "Next Steps:"
echo "1. Open dashboard in browser"
echo "2. Find 'Occupancy Monitor' section"
echo "3. Upload schedule (.xlsx file)"
echo "4. Watch smooth CPU-powered detection!"
echo ""
echo "View logs: docker-compose logs -f occupancy-monitor-processor"
echo "════════════════════════════════════════════════════════════════"

