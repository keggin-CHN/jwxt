#!/bin/bash

echo "========================================"
echo "  Installing Dependencies"
echo "========================================"
echo ""

echo "[1/2] Installing Python dependencies..."
pip3 install requests beautifulsoup4 pycryptodome flask flask-cors
echo ""

echo "[2/2] Installing frontend dependencies..."
cd frontend
npm install
cd ..
echo ""

echo "========================================"
echo "  Installation Complete"
echo "========================================"
echo ""
echo "You can now run ./start.sh to start the system"
echo ""
