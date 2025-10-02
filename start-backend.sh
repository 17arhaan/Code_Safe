#!/bin/bash

echo "🛡️  Starting Code Safe Backend Server..."
echo "========================================"
echo ""

# Activate virtual environment
source .venv/bin/activate

# Start the FastAPI server
cd backend
echo "Starting server at http://localhost:8000"
echo "API endpoints:"
echo "  - GET  /health"
echo "  - POST /api/analyze"
echo ""
echo "Press Ctrl+C to stop"
echo ""

python server.py

