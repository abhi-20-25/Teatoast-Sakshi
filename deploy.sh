#!/bin/bash

# Sakshi.AI Deployment Script for EC2 Ubuntu
# This script handles the complete deployment process

set -e  # Exit on any error

echo "========================================="
echo "   Sakshi.AI Deployment Script v1.0     "
echo "========================================="
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored messages
print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_info() {
    echo -e "ℹ️  $1"
}

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    print_error "Docker is not installed!"
    echo "Please install Docker first:"
    echo "  curl -fsSL https://get.docker.com -o get-docker.sh"
    echo "  sudo sh get-docker.sh"
    exit 1
fi

# Check if Docker Compose is installed
if ! command -v docker-compose &> /dev/null; then
    print_error "Docker Compose is not installed!"
    echo "Please install Docker Compose first:"
    echo "  sudo curl -L \"https://github.com/docker/compose/releases/latest/download/docker-compose-\$(uname -s)-\$(uname -m)\" -o /usr/local/bin/docker-compose"
    echo "  sudo chmod +x /usr/local/bin/docker-compose"
    exit 1
fi

# Check if PostgreSQL is running
print_info "Checking PostgreSQL..."
if ! sudo systemctl is-active --quiet postgresql; then
    print_error "PostgreSQL is not running!"
    echo "Please install and start PostgreSQL first:"
    echo "  ./setup_postgres.sh"
    exit 1
fi

# Test PostgreSQL connection
if ! PGPASSWORD='Tneural01' psql -h 127.0.0.1 -U postgres -d sakshi -c "SELECT 1;" &> /dev/null; then
    print_error "Cannot connect to PostgreSQL database 'sakshi'!"
    echo "Please run the PostgreSQL setup script:"
    echo "  ./setup_postgres.sh"
    exit 1
fi
print_success "PostgreSQL is running and accessible"

# Check if running in project directory
if [ ! -f "docker-compose.yml" ]; then
    print_error "docker-compose.yml not found!"
    echo "Please run this script from the Sakshi-21-OCT directory"
    exit 1
fi

# Check if config files exist
if [ ! -f "config/rtsp_links.txt" ]; then
    print_warning "config/rtsp_links.txt not found"
    print_info "Creating sample config file..."
    mkdir -p config
    cat > config/rtsp_links.txt <<EOF
# RTSP Camera Configuration
# Format: rtsp://url, Camera Name, App1, App2, App3
# Example:
# rtsp://admin:password@192.168.1.100:554/stream, Main Entrance, PeopleCounter, Security
# rtsp://admin:password@192.168.1.101:554/stream, Kitchen Area, KitchenCompliance
EOF
    print_warning "Please edit config/rtsp_links.txt and add your camera URLs"
fi

# Check if models directory exists
if [ ! -d "models" ]; then
    print_warning "models directory not found"
    print_info "Creating models directory..."
    mkdir -p models
    print_warning "Please add your model files (.pt) to the models/ directory"
fi

# Create static/detections directory if it doesn't exist
mkdir -p static/detections

# Show menu
echo ""
echo "What would you like to do?"
echo "1. Deploy (Build and start all services)"
echo "2. Restart (Restart existing containers)"
echo "3. Stop (Stop all services)"
echo "4. View logs"
echo "5. Check status"
echo "6. Rebuild (Rebuild and restart all services)"
echo "7. Clean up (Remove all containers and volumes)"
echo "8. Exit"
echo ""
read -p "Enter your choice [1-8]: " choice

case $choice in
    1)
        print_info "Building Docker images (this may take 10-20 minutes)..."
        docker-compose build
        print_success "Build completed"
        
        print_info "Starting all services..."
        docker-compose up -d
        print_success "Services started"
        
        echo ""
        print_info "Waiting for services to initialize..."
        sleep 10
        
        print_info "Checking service health..."
        docker-compose ps
        
        echo ""
        print_success "Deployment completed!"
        echo ""
        echo "📊 Access your dashboard at:"
        echo "   http://$(hostname -I | awk '{print $1}'):5001/dashboard"
        echo ""
        echo "📝 View logs with:"
        echo "   docker-compose logs -f"
        ;;
        
    2)
        print_info "Restarting all services..."
        docker-compose restart
        print_success "Services restarted"
        docker-compose ps
        ;;
        
    3)
        print_info "Stopping all services..."
        docker-compose down
        print_success "Services stopped"
        ;;
        
    4)
        print_info "Showing logs (Press Ctrl+C to exit)..."
        docker-compose logs -f
        ;;
        
    5)
        print_info "Service status:"
        docker-compose ps
        echo ""
        print_info "PostgreSQL status:"
        sudo systemctl status postgresql --no-pager -l
        ;;
        
    6)
        print_info "Stopping services..."
        docker-compose down
        
        print_info "Rebuilding images..."
        docker-compose build --no-cache
        
        print_info "Starting services..."
        docker-compose up -d
        
        print_success "Rebuild completed"
        docker-compose ps
        ;;
        
    7)
        print_warning "This will remove all containers and volumes!"
        read -p "Are you sure? (yes/no): " confirm
        if [ "$confirm" = "yes" ]; then
            print_info "Removing all containers..."
            docker-compose down -v
            
            print_info "Removing unused Docker resources..."
            docker system prune -f
            
            print_success "Cleanup completed"
        else
            print_info "Cleanup cancelled"
        fi
        ;;
        
    8)
        print_info "Exiting..."
        exit 0
        ;;
        
    *)
        print_error "Invalid choice!"
        exit 1
        ;;
esac

echo ""
print_info "Done!"

