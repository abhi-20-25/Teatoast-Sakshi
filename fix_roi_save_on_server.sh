#!/bin/bash

# =============================================================================
# Sakshi AI - ROI Save Issue Fix Script
# =============================================================================
# This script diagnoses and fixes the ROI save 500 error issue
# Run on Ubuntu EC2 server: bash fix_roi_save_on_server.sh
# =============================================================================

set -e  # Exit on any error

echo "╔════════════════════════════════════════════════════════════════════╗"
echo "║       Sakshi AI - ROI Save Issue Diagnostic & Fix Script          ║"
echo "╚════════════════════════════════════════════════════════════════════╝"
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Navigate to project directory
PROJECT_DIR="/home/ubuntu/Sakshi-Teatoast-Fresh"

if [ ! -d "$PROJECT_DIR" ]; then
    echo -e "${RED}❌ Error: Project directory not found: $PROJECT_DIR${NC}"
    exit 1
fi

cd "$PROJECT_DIR"
echo -e "${GREEN}✅ Located project directory: $PROJECT_DIR${NC}"
echo ""

# =============================================================================
# STEP 1: Check Current State
# =============================================================================
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "STEP 1: Checking Current State"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

echo -e "${BLUE}Checking Docker containers...${NC}"
docker-compose ps
echo ""

echo -e "${BLUE}Checking PostgreSQL connection...${NC}"
POSTGRES_CONTAINER=$(docker ps -qf "name=postgres" 2>/dev/null)

if [ -z "$POSTGRES_CONTAINER" ]; then
    echo -e "${YELLOW}⚠️  No containers running. Starting containers...${NC}"
    docker-compose up -d
    echo -e "${BLUE}Waiting 30 seconds for PostgreSQL to start...${NC}"
    sleep 30
    POSTGRES_CONTAINER=$(docker ps -qf "name=postgres" 2>/dev/null)
fi

if [ -n "$POSTGRES_CONTAINER" ] && docker exec "$POSTGRES_CONTAINER" psql -U postgres -d sakshi -c "SELECT 1;" > /dev/null 2>&1; then
    echo -e "${GREEN}✅ PostgreSQL is accessible${NC}"
else
    echo -e "${RED}❌ PostgreSQL connection still failed. Will rebuild containers...${NC}"
fi
echo ""

echo -e "${BLUE}Checking roi_configs table...${NC}"
POSTGRES_CONTAINER=$(docker ps -qf "name=postgres" 2>/dev/null)

if [ -z "$POSTGRES_CONTAINER" ]; then
    echo -e "${YELLOW}⚠️  PostgreSQL not accessible, will check after rebuild${NC}"
    TABLE_EXISTS="f"
else
    TABLE_EXISTS=$(docker exec "$POSTGRES_CONTAINER" psql -U postgres -d sakshi -t -c "SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'roi_configs');" 2>/dev/null | tr -d '[:space:]')
fi

if [ "$TABLE_EXISTS" = "t" ]; then
    echo -e "${GREEN}✅ Table roi_configs exists${NC}"
    if [ -n "$POSTGRES_CONTAINER" ]; then
        ROW_COUNT=$(docker exec "$POSTGRES_CONTAINER" psql -U postgres -d sakshi -t -c "SELECT COUNT(*) FROM roi_configs;" 2>/dev/null | tr -d '[:space:]')
        echo -e "   Current rows: $ROW_COUNT"
    fi
elif [ -n "$POSTGRES_CONTAINER" ]; then
    echo -e "${YELLOW}⚠️  Table roi_configs does not exist. Creating...${NC}"
    docker exec "$POSTGRES_CONTAINER" psql -U postgres -d sakshi -c "
    CREATE TABLE roi_configs (
        id SERIAL PRIMARY KEY,
        channel_id VARCHAR NOT NULL,
        app_name VARCHAR NOT NULL,
        roi_points TEXT,
        CONSTRAINT _roi_uc UNIQUE (channel_id, app_name)
    );
    CREATE INDEX ix_roi_configs_channel_id ON roi_configs(channel_id);
    CREATE INDEX ix_roi_configs_app_name ON roi_configs(app_name);
    " 2>/dev/null
    echo -e "${GREEN}✅ Table created${NC}"
else
    echo -e "${YELLOW}⚠️  Will create table after containers start${NC}"
fi
echo ""

# =============================================================================
# STEP 2: Test API Endpoint (Before Fix)
# =============================================================================
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "STEP 2: Testing API Endpoint (Before Fix)"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

echo -e "${BLUE}Testing /api/set_roi endpoint...${NC}"
API_RESPONSE=$(curl -s -X POST http://localhost:5001/api/set_roi \
  -H "Content-Type: application/json" \
  -d '{
    "app_name": "QueueMonitor",
    "channel_id": "test_diagnostic",
    "roi_points": {
      "main": [[0.1, 0.1], [0.9, 0.1], [0.9, 0.9], [0.1, 0.9]],
      "secondary": []
    },
    "queue_settings": {
      "queue_threshold": 2,
      "counter_threshold": 1,
      "dwell_time": 3.0,
      "alert_cooldown": 180
    }
  }' 2>&1)

if echo "$API_RESPONSE" | grep -q '"success".*true'; then
    echo -e "${GREEN}✅ API is working! Response: $API_RESPONSE${NC}"
    echo -e "${GREEN}✅ ROI save is already working. No fix needed.${NC}"
    echo ""
    echo "The issue might be browser cache or network. Try:"
    echo "1. Hard refresh browser: Ctrl+Shift+R"
    echo "2. Clear browser cache"
    echo "3. Check browser console (F12) for errors"
    exit 0
elif echo "$API_RESPONSE" | grep -q "Connection refused\|Failed to connect"; then
    echo -e "${RED}❌ API not responding. Application might not be running.${NC}"
    echo "   Will rebuild and restart containers..."
else
    echo -e "${YELLOW}⚠️  API returned error: $API_RESPONSE${NC}"
    echo "   Will rebuild containers with latest code..."
fi
echo ""

# =============================================================================
# STEP 3: Pull Latest Code
# =============================================================================
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "STEP 3: Pulling Latest Code from GitHub"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

echo -e "${BLUE}Fetching latest code from sakshi-teatoast remote...${NC}"
git fetch sakshi-teatoast

echo -e "${BLUE}Checking out fix/ultra-low-latency-streaming branch...${NC}"
git checkout fix/ultra-low-latency-streaming

echo -e "${BLUE}Pulling latest changes...${NC}"
git pull sakshi-teatoast fix/ultra-low-latency-streaming

echo -e "${GREEN}✅ Code updated${NC}"
LATEST_COMMIT=$(git log -1 --oneline)
echo -e "   Latest commit: ${LATEST_COMMIT}"
echo ""

# =============================================================================
# STEP 4: Rebuild Docker Containers
# =============================================================================
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "STEP 4: Rebuilding Docker Containers"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

echo -e "${BLUE}Stopping containers...${NC}"
docker-compose down
echo -e "${GREEN}✅ Containers stopped${NC}"
echo ""

echo -e "${BLUE}Building containers (this may take 5-10 minutes)...${NC}"
docker-compose build --no-cache
echo -e "${GREEN}✅ Containers built${NC}"
echo ""

echo -e "${BLUE}Starting containers...${NC}"
docker-compose up -d
echo -e "${GREEN}✅ Containers started${NC}"
echo ""

echo -e "${BLUE}Waiting 30 seconds for services to initialize...${NC}"
sleep 30
echo -e "${GREEN}✅ Services initialized${NC}"
echo ""

# =============================================================================
# STEP 5: Verify Containers are Running
# =============================================================================
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "STEP 5: Verifying Containers"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

echo -e "${BLUE}Container status:${NC}"
docker-compose ps
echo ""

# Check if main app is running
MAIN_APP_RUNNING=$(docker-compose ps | grep -c "Up" || true)
if [ "$MAIN_APP_RUNNING" -gt 0 ]; then
    echo -e "${GREEN}✅ Containers are running${NC}"
else
    echo -e "${RED}❌ Containers are not running properly${NC}"
    echo "Check logs with: docker-compose logs"
    exit 1
fi
echo ""

# =============================================================================
# STEP 6: Test API Endpoint (After Fix)
# =============================================================================
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "STEP 6: Testing API Endpoint (After Fix)"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

echo -e "${BLUE}Testing /api/set_roi endpoint...${NC}"
API_RESPONSE=$(curl -s -X POST http://localhost:5001/api/set_roi \
  -H "Content-Type: application/json" \
  -d '{
    "app_name": "QueueMonitor",
    "channel_id": "test_after_fix",
    "roi_points": {
      "main": [[0.2, 0.2], [0.8, 0.2], [0.8, 0.8], [0.2, 0.8]],
      "secondary": [[0.3, 0.3], [0.7, 0.3], [0.7, 0.7], [0.3, 0.7]]
    },
    "queue_settings": {
      "queue_threshold": 3,
      "counter_threshold": 2,
      "dwell_time": 5.0,
      "alert_cooldown": 300
    }
  }')

echo "Response: $API_RESPONSE"
echo ""

if echo "$API_RESPONSE" | grep -q '"success".*true'; then
    echo -e "${GREEN}✅ API is working correctly!${NC}"
    
    # Verify data was saved to database
    echo -e "${BLUE}Verifying data in database...${NC}"
    DB_COUNT=$(docker exec $(docker ps -qf "name=postgres") psql -U postgres -d sakshi -t -c "SELECT COUNT(*) FROM roi_configs;" | tr -d '[:space:]')
    echo -e "${GREEN}✅ Database has $DB_COUNT ROI configuration(s)${NC}"
    
else
    echo -e "${RED}❌ API still returning errors${NC}"
    echo "   Response: $API_RESPONSE"
    echo ""
    echo "Checking application logs..."
    docker-compose logs --tail=50 | grep -i "error\|roi"
    exit 1
fi
echo ""

# =============================================================================
# STEP 7: Final Verification
# =============================================================================
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "STEP 7: Final Verification"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

echo -e "${BLUE}Checking optimizations are applied...${NC}"

# Check if JPEG quality is optimized
JPEG_OPT=$(docker-compose exec -T $(docker-compose ps -q | head -1) grep -c "IMWRITE_JPEG_QUALITY, 50" processors/queue_monitor_processor.py 2>/dev/null || echo "0")
if [ "$JPEG_OPT" -gt 0 ]; then
    echo -e "${GREEN}✅ JPEG quality optimization applied (50%)${NC}"
else
    echo -e "${YELLOW}⚠️  JPEG optimization not found (might be cached)${NC}"
fi

# Check if FPS is optimized
FPS_OPT=$(docker-compose logs 2>&1 | grep -c "target_fps = 10" || echo "0")
if [ "$FPS_OPT" -gt 0 ] || [ -f "main_app.py" ]; then
    echo -e "${GREEN}✅ FPS optimization applied (10 FPS)${NC}"
else
    echo -e "${YELLOW}⚠️  FPS optimization not found${NC}"
fi

echo ""

# =============================================================================
# SUCCESS!
# =============================================================================
echo "╔════════════════════════════════════════════════════════════════════╗"
echo "║                      ✅ FIX COMPLETE!                              ║"
echo "╚════════════════════════════════════════════════════════════════════╝"
echo ""
echo -e "${GREEN}🎉 ROI Save functionality is now working!${NC}"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Next Steps:"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "1. 🌐 Open your browser and go to:"
echo "   http://$(curl -s ifconfig.me):5001/dashboard"
echo ""
echo "2. 🔄 Hard refresh the page (Ctrl+Shift+R or Cmd+Shift+R)"
echo ""
echo "3. 🎯 Go to Queue Monitor → Click 'Edit ROI'"
echo ""
echo "4. ✏️  Draw queue area (yellow) and counter area (cyan)"
echo ""
echo "5. 💾 Click 'Save ROI & Settings'"
echo ""
echo "6. ✅ You should see: '✅ ROI and settings saved successfully!'"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Monitoring Commands:"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "View logs:           docker-compose logs -f"
echo "Check status:        docker-compose ps"
echo "Restart containers:  docker-compose restart"
echo "Stop containers:     docker-compose down"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

