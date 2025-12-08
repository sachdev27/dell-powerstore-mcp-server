#!/bin/bash

# Start the PowerStore MCP server in HTTP/SSE mode for n8n

# Activate virtual environment if it exists
if [ -d ".venv" ]; then
    source .venv/bin/activate
elif [ -d "venv" ]; then
    source venv/bin/activate
fi

# Default port
PORT=${PORT:-3000}

echo "Starting PowerStore MCP Server (HTTP/SSE mode)"
echo "Server will be available at: http://localhost:$PORT"
echo "SSE endpoint: http://localhost:$PORT/sse"
echo "Health check: http://localhost:$PORT/health"
echo ""

# Run the HTTP server
uvicorn powerstore_mcp.http_server:app --host 0.0.0.0 --port $PORT
