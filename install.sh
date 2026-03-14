#!/usr/bin/env bash
echo "======================================"
echo "Photon Laser Tag - Installation Script"
echo "Software Engineering"
echo "======================================"
echo ""

set -e
cd "$(dirname "$0")"

sudo apt update
sudo apt install -y \
  python3 \
  python3-tk \
  python3-pil \
  python3-pil.imagetk \
  python3-psycopg2 \
  postgresql

sudo systemctl enable postgresql >/dev/null 2>&1 || true
sudo systemctl start postgresql

echo ""
echo "Install complete. Run: python3 main.py"
