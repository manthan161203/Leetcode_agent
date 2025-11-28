#!/bin/bash

# LeetCode GitHub Agent - Startup Script

echo "🚀 Starting LeetCode GitHub Agent..."
echo ""

# Check if virtual environment exists
if [ ! -d ".venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv .venv
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source .venv/bin/activate

# Install dependencies
echo "📥 Installing dependencies..."
pip install -q -r requirements.txt

# Check for .env file
if [ ! -f ".env" ]; then
    echo "⚠️  No .env file found. Creating from .env.example..."
    cp .env.example .env
    echo "⚠️  Please edit .env and add your GOOGLE_API_KEY"
    echo ""
    read -p "Press Enter to continue after editing .env..."
fi

# Load environment variables
echo "🔐 Loading environment variables..."
export $(cat .env | grep -v '^#' | xargs)

# Validate GOOGLE_API_KEY
if [ -z "$GOOGLE_API_KEY" ] || [ "$GOOGLE_API_KEY" = "your_google_api_key_here" ]; then
    echo "❌ ERROR: GOOGLE_API_KEY not set in .env file"
    echo "Please edit .env and add your actual Google API key"
    exit 1
fi

echo "✅ Environment variables loaded"
echo ""

# Start backend in background
echo "🔄 Starting FastAPI backend..."
uvicorn app:app --reload --port 8000 &
BACKEND_PID=$!

# Wait for backend to start
echo "⏳ Waiting for backend to start..."
sleep 3

# Start frontend
echo "🎨 Starting Streamlit frontend..."
echo ""
echo "================================"
echo "✅ Application is starting!"
echo "================================"
echo "Frontend: http://localhost:8501"
echo "Backend: http://localhost:8000/docs"
echo "================================"
echo ""

streamlit run frontend.py

# Cleanup on exit
echo ""
echo "🛑 Shutting down..."
kill $BACKEND_PID
