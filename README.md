# Dell PowerStore MCP Server

[![CI](https://github.com/sachdev27/powerstore-mcp-server/actions/workflows/ci.yml/badge.svg)](https://github.com/sachdev27/powerstore-mcp-server/actions/workflows/ci.yml)
[![Python Version](https://img.shields.io/pypi/pyversions/powerstore-mcp-server.svg)](https://pypi.org/project/powerstore-mcp-server/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)

A [Model Context Protocol (MCP)](https://modelcontextprotocol.io/) server for Dell PowerStore that automatically generates tools from OpenAPI specifications with a credential-free architecture. Enables AI assistants like Claude and automation platforms like n8n to interact with PowerStore storage arrays.

## ✨ Features

| Feature | Description |
|---------|-------------|
| 🔄 **Automatic Tool Generation** | Dynamically generates 262+ MCP tools from Dell PowerStore OpenAPI specs |
| 🔐 **Credential-Free Architecture** | No stored credentials - pass host/username/password with each tool call |
| 🌐 **Multi-Host Support** | Manage multiple PowerStore instances from a single server |
| 🛡️ **Safe Operations** | GET-only operations for read-only PowerStore access |
| 🔌 **Multiple Transports** | HTTP/SSE for n8n, stdio for Claude Desktop |
| 📊 **Health Monitoring** | Built-in health checks and metrics endpoints |
| 🐳 **Docker Ready** | Production-ready container images |

## 📋 Table of Contents

- [Quick Start](#-quick-start)
- [Installation](#-installation)
- [Configuration](#-configuration)
- [Usage](#-usage)
- [Integration](#-integration)
- [Available Tools](#-available-tools)
- [Architecture](#-architecture)
- [Development](#-development)
- [Contributing](#-contributing)
- [License](#-license)

## 🚀 Quick Start

```bash
# Clone and install
git clone https://github.com/sachdev27/powerstore-mcp-server.git
cd powerstore-mcp-server
pip install -e .

# Run HTTP/SSE server (for n8n)
powerstore-mcp-http

# Or run stdio server (for Claude Desktop)
powerstore-mcp
```

## 📦 Installation

### From PyPI (Recommended)

```bash
pip install powerstore-mcp-server
```

### From Source

```bash
# Clone the repository
git clone https://github.com/sachdev27/powerstore-mcp-server.git
cd powerstore-mcp-server

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # On macOS/Linux
# .venv\Scripts\activate   # On Windows

# Install in development mode
pip install -e ".[dev]"
```

### Using Docker

```bash
docker pull ghcr.io/sachdev27/powerstore-mcp-server:latest

# Run with SSE transport
docker run -p 3000:3000 ghcr.io/sachdev27/powerstore-mcp-server:latest
```

### Requirements

- **Python**: 3.10, 3.11, 3.12, or 3.13
- **Dell PowerStore**: Any supported version (for actual operations)

## ⚙️ Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `LOG_LEVEL` | Logging level (debug, info, warning, error) | `info` |
| `LOG_FORMAT` | Log format (text, json) | `text` |
| `OPENAPI_SPEC_PATH` | Path to OpenAPI specification | `./openapi.json` |
| `HTTP_PORT` | HTTP server port | `3000` |
| `HTTP_HOST` | HTTP server host | `0.0.0.0` |

### Example `.env` File

```env
LOG_LEVEL=info
LOG_FORMAT=json
HTTP_PORT=3000
```

> ⚠️ **Important:** PowerStore credentials are NOT stored in configuration. They are passed securely with each tool call.

## 📖 Usage

### HTTP/SSE Mode (for n8n and Web Clients)

```bash
# Using the CLI
powerstore-mcp-http

# Using uvicorn directly
uvicorn powerstore_mcp.http_server:app --host 0.0.0.0 --port 3000

# Using the start script
./start-http.sh
```

The server provides:
- **SSE Endpoint**: `http://localhost:3000/sse`
- **Health Check**: `http://localhost:3000/health`
- **Metrics**: `http://localhost:3000/health` (detailed JSON response)

### stdio Mode (for Claude Desktop)

```bash
# Using the CLI
powerstore-mcp

# Using Python module
python -m powerstore_mcp.main

# Using the start script
./start-python.sh
```

### Docker Compose

```bash
# Start the server
docker-compose up -d

# View logs
docker-compose logs -f

# Stop the server
docker-compose down
```

## 🔗 Integration

### n8n AI Agent

1. Add an **MCP Client** node to your n8n workflow
2. Configure the connection:
   - **Transport**: SSE
   - **URL**: `http://localhost:3000/sse`
3. The 262 PowerStore tools will be available to AI agents

### Claude Desktop

Add to your Claude Desktop configuration (`claude_desktop_config.json`):

```json
{
  "mcpServers": {
    "dell-powerstore": {
      "command": "powerstore-mcp",
      "args": []
    }
  }
}
```

Or with explicit Python path:

```json
{
  "mcpServers": {
    "dell-powerstore": {
      "command": "/path/to/venv/bin/python",
      "args": ["-m", "powerstore_mcp.main"]
    }
  }
}
```

### Custom MCP Clients

```python
import asyncio
from mcp import ClientSession
from mcp.client.sse import sse_client

async def main():
    async with sse_client("http://localhost:3000/sse") as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()

            # List available tools
            tools = await session.list_tools()
            print(f"Found {len(tools.tools)} tools")

            # Call a tool
            result = await session.call_tool("getAppliance", {
                "host": "powerstore.example.com",
                "username": "admin",
                "password": "password"
            })
            print(result)

asyncio.run(main())
```

## 🔧 Available Tools

The server dynamically generates **262 tools** from the PowerStore OpenAPI specification.

### Authentication Parameters

Every tool requires these authentication parameters:

| Parameter | Type | Description |
|-----------|------|-------------|
| `host` | string | PowerStore hostname or IP |
| `username` | string | PowerStore username |
| `password` | string | PowerStore password |

### Tool Categories

| Category | Example Tools | Description |
|----------|--------------|-------------|
| **Storage** | `getVolume`, `getHost`, `getVolume_group` | Volume and host management |
| **System** | `getAppliance`, `getCluster`, `getNode` | System information |
| **Network** | `getNetwork`, `getIp_port`, `getFc_port` | Network configuration |
| **File Services** | `getNas_server`, `getFile_system`, `getNfs_export` | File storage |
| **Protection** | `getSnapshot_rule`, `getReplication_rule` | Data protection |
| **Monitoring** | `getAlert`, `getEvent`, `getPerformance_rule` | Alerts and events |

### Query Parameters

All collection endpoints support PowerStore query parameters:

```json
{
  "host": "powerstore.example.com",
  "username": "admin",
  "password": "password",
  "select": "id,name,size",
  "limit": 100,
  "offset": 0,
  "order": "name.asc"
}
```

## 🏗️ Architecture

### Credential-Free Design

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│   AI Client     │────▶│   MCP Server    │────▶│   PowerStore    │
│ (Claude/n8n)    │     │ (No Credentials)│     │    Array        │
└─────────────────┘     └─────────────────┘     └─────────────────┘
         │                      │
         │   Tool Call with     │   Per-Request
         │   Credentials        │   Authentication
         ▼                       ▼
    {host, user, pass}      Basic Auth Header
```

### Key Design Principles

- **No Stored Credentials**: Server starts without any PowerStore connection
- **Per-Request Auth**: Each tool call includes host/username/password
- **Fresh Sessions**: New API client created for each request
- **Multi-Host Ready**: Easily manage multiple PowerStore instances

### Module Structure

```
powerstore_mcp/
├── __init__.py          # Package initialization and version
├── api_client.py        # Async PowerStore API client with retry logic
├── config.py            # Configuration management with validation
├── exceptions.py        # Custom exception hierarchy
├── http_server.py       # HTTP/SSE transport server
├── logging_config.py    # Structured logging configuration
├── main.py              # stdio transport entry point
├── server.py            # Core MCP server with tool handlers
└── tool_generator.py    # OpenAPI parser and tool generator
```

## 🧪 Development

### Setup Development Environment

```bash
# Clone and install with dev dependencies
git clone https://github.com/sachdev27/powerstore-mcp-server.git
cd powerstore-mcp-server
pip install -e ".[dev]"

# Install pre-commit hooks
pre-commit install
```

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=powerstore_mcp --cov-report=html

# Run specific test file
pytest tests/test_tool_generator.py -v
```

### Code Quality

```bash
# Format code
black powerstore_mcp tests

# Lint code
ruff check powerstore_mcp tests

# Type checking
mypy powerstore_mcp

# Security scan
bandit -r powerstore_mcp
```

### Building

```bash
# Build distribution packages
python -m build

# Build Docker image
docker build -t powerstore-mcp-server .
```

## 🤝 Contributing

Contributions are welcome! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 📚 Additional Resources

- [Model Context Protocol Documentation](https://modelcontextprotocol.io/)
- [Dell PowerStore Documentation](https://www.dell.com/support/home/en-us/product-support/product/powerstore)
- [n8n MCP Integration Guide](https://docs.n8n.io/)

---

<p align="center">
  Made with ❤️ for the storage automation community
</p>
