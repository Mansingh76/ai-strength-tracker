#!/bin/bash

echo "🏋️ AI Strength Tracker - Starting Setup..."
echo "=================================="

# Create data directory
mkdir -p data

# Install requirements if not already installed
if [ ! -f ".installed" ]; then
    echo "📦 Installing dependencies..."
    pip install -r requirements.txt
    touch .installed
    echo "✅ Dependencies installed!"
fi

# Check if running in Codespaces
if [ -n "$CODESPACES" ]; then
    echo "🌐 Running in GitHub Codespaces"
    echo "📱 App will be available at your Codespaces URL on port 8501"
    streamlit run app.py --server.port 8501 --server.address 0.0.0.0 --server.headless true
else
    echo "💻 Running locally"
    echo "🌐 App will open at http://localhost:8501"
    streamlit run app.py
fi
