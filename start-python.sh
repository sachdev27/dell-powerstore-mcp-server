#!/bin/bash
# Quick start script for Python implementation

set -e

echo "🐍 Dell PowerStore MCP Server (Python)"
echo "======================================"
echo ""

# Check Python version
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed"
    exit 1
fi

PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
echo "✅ Python $PYTHON_VERSION detected"

# Check if openapi.json exists
if [ ! -f "openapi.json" ]; then
    echo "❌ openapi.json not found in current directory"
    exit 1
fi
echo "✅ openapi.json found"

# Check if .env exists, create from template if not
if [ ! -f ".env" ]; then
    if [ -f ".env.python" ]; then
        echo "📝 Creating .env from .env.python template"
        cp .env.python .env
    else
        echo "❌ Neither .env nor .env.python found"
        exit 1
    fi
fi
echo "✅ .env configuration found"

# Install dependencies
echo ""
echo "📦 Installing Python dependencies..."
if command -v uv &> /dev/null; then
    echo "Using uv for faster installation..."
    uv pip install -r requirements.txt
else
    python3 -m pip install -r requirements.txt
fi

echo ""
echo "🚀 Starting server..."
echo "   Endpoint: http://localhost:3000/mcp"
echo "   Health: http://localhost:3000/health"
echo ""
echo "Press Ctrl+C to stop"
echo ""

# Run the server
python3 -m powerstore_mcp.main
