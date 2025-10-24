#!/bin/bash

# Sakshi.AI PostgreSQL Setup Script for EC2 Ubuntu
# This script automates the PostgreSQL installation and configuration

set -e  # Exit on any error

echo "======================================"
echo "  Sakshi.AI PostgreSQL Setup Script  "
echo "======================================"
echo ""

# Check if running as root
if [ "$EUID" -eq 0 ]; then 
   echo "❌ Please do not run this script as root or with sudo"
   echo "   Run it as a regular user with sudo privileges"
   exit 1
fi

# Update system
echo "📦 Updating system packages..."
sudo apt update

# Install PostgreSQL
echo "🗄️  Installing PostgreSQL..."
sudo apt install -y postgresql postgresql-contrib

# Start and enable PostgreSQL
echo "▶️  Starting PostgreSQL service..."
sudo systemctl start postgresql
sudo systemctl enable postgresql

# Wait for PostgreSQL to be ready
sleep 3

# Create database and user
echo "🔧 Creating database and user..."
sudo -u postgres psql <<EOF
-- Drop database if exists (for clean reinstall)
DROP DATABASE IF EXISTS sakshi;

-- Create database
CREATE DATABASE sakshi;

-- Set password for postgres user
ALTER USER postgres WITH PASSWORD 'Tneural01';
ALTER USER postgres WITH SUPERUSER;

-- Grant privileges
GRANT ALL PRIVILEGES ON DATABASE sakshi TO postgres;

-- List databases
\l

EOF

# Find PostgreSQL version
PG_VERSION=$(ls /etc/postgresql/ | head -n 1)
echo "📌 PostgreSQL version: $PG_VERSION"

# Configure PostgreSQL to listen on localhost
echo "🔧 Configuring PostgreSQL for TCP connections..."
sudo sed -i "s/#listen_addresses = 'localhost'/listen_addresses = 'localhost,127.0.0.1'/" /etc/postgresql/$PG_VERSION/main/postgresql.conf

# Add authentication rules if not already present
if ! grep -q "host.*sakshi.*postgres.*127.0.0.1" /etc/postgresql/$PG_VERSION/main/pg_hba.conf; then
    echo "host    sakshi          postgres        127.0.0.1/32            md5" | sudo tee -a /etc/postgresql/$PG_VERSION/main/pg_hba.conf
    echo "host    all             postgres        127.0.0.1/32            md5" | sudo tee -a /etc/postgresql/$PG_VERSION/main/pg_hba.conf
fi

# Restart PostgreSQL
echo "🔄 Restarting PostgreSQL..."
sudo systemctl restart postgresql

# Wait for restart
sleep 2

# Test connection
echo ""
echo "🧪 Testing PostgreSQL connection..."
if PGPASSWORD='Tneural01' psql -h 127.0.0.1 -U postgres -d sakshi -c "SELECT 'Connection successful!' as status;" 2>/dev/null; then
    echo ""
    echo "✅ PostgreSQL setup completed successfully!"
    echo ""
    echo "Database Details:"
    echo "  Host: 127.0.0.1"
    echo "  Port: 5432"
    echo "  Database: sakshi"
    echo "  Username: postgres"
    echo "  Password: Tneural01"
    echo ""
    echo "Connection String:"
    echo "  postgresql+psycopg2://postgres:Tneural01@127.0.0.1:5432/sakshi"
    echo ""
else
    echo ""
    echo "⚠️  Connection test failed. Please check the logs:"
    echo "  sudo journalctl -u postgresql -n 50"
    exit 1
fi

