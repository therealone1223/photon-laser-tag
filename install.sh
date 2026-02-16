#!/bin/bash

echo "======================================"
echo "Photon Laser Tag - Installation Script"
echo "Software Engineering"
echo "======================================"
echo ""

set -e
cd "$(dirname "$0")"

sudo apt update
sudo apt install -y \
  python3 python3-tk \
  python3-pil python3-pil.imagetk \
  python3-psycopg2 \
  postgresql

sudo systemctl enable postgresql >/dev/null 2>&1 || true
sudo systemctl start postgresql

sudo -u postgres psql -tAc "SELECT 1 FROM pg_database WHERE datname='photon';" | grep -q 1 \
  || sudo -u postgres createdb photon

if [ -f "player.sql" ]; then
  sudo -u postgres psql photon -f player.sql
else
  sudo -u postgres psql photon -c "CREATE TABLE IF NOT EXISTS players (id INTEGER PRIMARY KEY, codename VARCHAR(255));"
fi

echo "Install complete. Run: python3 src/main.py"
