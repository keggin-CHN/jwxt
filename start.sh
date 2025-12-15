#!/bin/bash

echo "========================================"
echo "  Grade Monitor System v2.0"
echo "========================================"
echo ""

echo "[1/3] Checking Python dependencies..."
python3 -c "import requests, bs4, flask, flask_cors" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "Missing Python dependencies, installing..."
    pip3 install requests beautifulsoup4 pycryptodome flask flask-cors
else
    echo "✓ Python dependencies ready"
fi
echo ""

echo "[2/3] Checking frontend dependencies..."
cd frontend
if [ ! -d "node_modules" ]; then
    echo "Frontend dependencies not installed, installing..."
    npm install
else
    echo "✓ Frontend dependencies ready"
fi
cd ..
echo ""

echo "[3/3] Starting services..."
echo "✓ Starting backend monitor service..."
python3 monitor.py &
BACKEND_PID=$!

sleep 3

echo "✓ Starting frontend interface..."
cd frontend
npm start &
FRONTEND_PID=$!

echo ""
echo "========================================"
echo "  Startup Complete"
echo "========================================"
echo ""
echo "Backend API: http://localhost:5000"
echo "Frontend UI: http://localhost:3000"
echo ""
echo "Backend PID: $BACKEND_PID"
echo "Frontend PID: $FRONTEND_PID"
echo ""
echo "Press Ctrl+C to stop all services"
echo ""

trap "kill $BACKEND_PID $FRONTEND_PID 2>/dev/null; exit" INT TERM

wait
