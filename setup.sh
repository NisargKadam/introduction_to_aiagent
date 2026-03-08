#!/bin/bash
echo "============================================"
echo "  AI Agent Demo - Setup"
echo "  Author: Nisarg Kadam"
echo "============================================"
echo

# Create virtual environment
echo "[1/3] Creating virtual environment..."
python3 -m venv .venv
source .venv/bin/activate

# Install dependencies
echo "[2/3] Installing dependencies..."
pip install -r requirements.txt

# Check for .env
echo
if [ ! -f .env ]; then
    echo "[3/3] Creating .env from template..."
    cp .env.example .env
    echo
    echo "========================================"
    echo "  IMPORTANT: Edit .env and add your"
    echo "  OpenAI API key before running!"
    echo "========================================"
else
    echo "[3/3] .env already exists - skipping"
fi

echo
echo "Setup complete! Run the server with:"
echo "  source .venv/bin/activate"
echo "  python app.py"
