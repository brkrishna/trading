#!/bin/bash

# Trading Scanner Streamlit Dashboard Launcher
# This script activates the virtual environment and starts the Streamlit app

echo "🚀 Starting Trading Scanner Dashboard..."

# Activate virtual environment
if [ -d ".venv" ]; then
    echo "📦 Activating virtual environment..."
    source .venv/Scripts/activate
else
    echo "❌ Virtual environment not found. Please run: python -m venv .venv"
    exit 1
fi

# Install/update dependencies
echo "📚 Installing dependencies..."
pip install -q -r requirements.txt

# Start Streamlit
echo "🌐 Launching Streamlit dashboard..."
echo "💡 Dashboard will be available at: http://localhost:8501"
echo "💡 Use Ctrl+C to stop the server"
echo ""

streamlit run streamlit_app.py --server.port 8501 --server.address localhost