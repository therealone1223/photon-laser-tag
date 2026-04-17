#!/usr/bin/env bash
set -euo pipefail

echo "======================================"
echo "Photon Laser Tag - Installation Script"
echo "Software Engineering"
echo "======================================"
echo ""

PROJECT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$PROJECT_DIR"

echo "[1/6] Updating package list..."
sudo apt update

echo "[2/6] Installing system packages..."
sudo apt install -y \
  python3 \
  python3-pip \
  python3-pygame \
  python3-venv \
  python3-tk \
  python3-pil \
  python3-pil.imagetk \
  python3-psycopg2 \
  postgresql \
  postgresql-contrib

echo "[3/6] Enabling and starting PostgreSQL..."
sudo systemctl enable postgresql >/dev/null 2>&1 || true
sudo systemctl start postgresql

echo "[4/6] Setting up PostgreSQL user and database..."
sudo -u postgres psql -tc "SELECT 1 FROM pg_roles WHERE rolname='student'" | grep -q 1 || \
  sudo -u postgres psql -c "CREATE ROLE student LOGIN PASSWORD 'student';"

sudo -u postgres psql -tc "SELECT 1 FROM pg_database WHERE datname='photon'" | grep -q 1 || \
  sudo -u postgres psql -c "CREATE DATABASE photon OWNER student;"

echo "[5/6] Creating players table if needed..."
sudo -u postgres psql -d photon <<'SQL'
CREATE TABLE IF NOT EXISTS players (
    id INTEGER PRIMARY KEY,
    codename VARCHAR(255) NOT NULL
);

ALTER DATABASE photon OWNER TO student;
GRANT ALL PRIVILEGES ON DATABASE photon TO student;
GRANT ALL PRIVILEGES ON TABLE players TO student;
SQL

echo "[6/6] Final checks..."
if [ ! -f "$PROJECT_DIR/src/main.py" ]; then
  echo "Warning: src/main.py was not found."
else
  echo "Application entry point found: src/main.py"
fi

echo ""
echo "Install complete."
echo "Run the game with:"
echo "  python3 src/main.py"
