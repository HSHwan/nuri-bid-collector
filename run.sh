#!/bin/bash

set -e

echo "🚀 Starting Nuri Bid Collector Setup..."

if ! command -v python3 &> /dev/null
then
    echo "[ERROR] Python3 could not be found. Please install Python 3.9+"
    exit 1
fi

if [ ! -d "venv" ]; then
    echo "[INFO] Creating virtual environment..."
    python3 -m venv venv
fi

source venv/bin/activate

if [ -f "requirements.txt" ]; then
    echo "[INFO] Installing dependencies..."
    pip install -r requirements.txt
else
    echo "[WARNING] requirements.txt not found!"
fi

echo "[INFO] Installing Playwright chromium..."
playwright install chromium

echo "[INFO] Running Crawler..."
export PYTHONPATH=$(pwd)
python3 src/main.py