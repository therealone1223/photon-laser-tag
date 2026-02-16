#!/bin/bash

echo "======================================"
echo "Photon Laser Tag - Installation Script"
echo "Software Engineering"
echo "======================================"
echo ""

echo "Installing system dependencies..."
sudo apt update
sudo apt upgrade -y

echo ""
echo "Installing Python3 and pip..."
sudo apt install python3 python3-pip python3-tk -y

echo ""
echo "Verifying Python installation..."
python3 --version

echo ""
echo "Installing PostgreSQL and dependencies..."
sudo apt-get update
sudo apt-get install postgresql libpq-dev -y
sudo apt-get install python3-psycopg2 python3-pil python3-pil.imagetk -y

echo ""
echo "Installing Python packages..."
pip install psycopg2

echo ""
echo "Starting PostgreSQL service..."
sudo systemctl start postgresql
sudo systemctl enable postgresql

echo ""
echo "Setting up database..."
sudo -u postgres psql << PSQL_EOF
CREATE DATABASE photon;
\c photon
CREATE TABLE IF NOT EXISTS players (
    id INTEGER PRIMARY KEY,
    codename VARCHAR(255)
);
GRANT ALL PRIVILEGES ON DATABASE photon TO student;
PSQL_EOF

echo ""
echo "======================================"
echo "Installation Complete!"
echo "======================================"
echo ""
echo "To run the application:"
echo "  cd src"
echo "  python3 main.py"
echo ""
