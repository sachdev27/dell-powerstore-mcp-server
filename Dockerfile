# syntax=docker/dockerfile:1

# =============================================================================
# Dell PowerStore MCP Server - Production Dockerfile
# Multi-stage build for optimal image size and security
# =============================================================================

# -----------------------------------------------------------------------------
# Stage 1: Builder - Install dependencies and build wheel
# -----------------------------------------------------------------------------
FROM python:3.11-slim AS builder

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

WORKDIR /build

# Install build dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        gcc \
        libffi-dev \
    && rm -rf /var/lib/apt/lists/*

# Create virtual environment
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Install Python dependencies
COPY requirements.txt .
RUN pip install --upgrade pip setuptools wheel && \
    pip install -r requirements.txt

# Copy and install the application
COPY pyproject.toml .
COPY powerstore_mcp/ ./powerstore_mcp/
RUN pip install .

# -----------------------------------------------------------------------------
# Stage 2: Runtime - Minimal production image
# -----------------------------------------------------------------------------
FROM python:3.11-slim AS runtime

# Labels for container metadata (OCI standard)
LABEL org.opencontainers.image.title="Dell PowerStore MCP Server" \
      org.opencontainers.image.description="Model Context Protocol server for Dell PowerStore storage management" \
      org.opencontainers.image.version="1.0.0" \
      org.opencontainers.image.vendor="Dell Technologies" \
      org.opencontainers.image.licenses="MIT" \
      org.opencontainers.image.source="https://github.com/sachdev27/dell-powerstore-mcp-server" \
      org.opencontainers.image.documentation="https://github.com/sachdev27/dell-powerstore-mcp-server#readme"

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONFAULTHANDLER=1 \
    # Application settings
    LOG_LEVEL=info \
    LOG_FORMAT=json \
    HTTP_HOST=0.0.0.0 \
    HTTP_PORT=3000 \
    LOCAL_OPENAPI_SPEC_PATH=/app/openapi.json \
    # Paths
    PATH="/opt/venv/bin:$PATH" \
    APP_HOME=/app

# Create non-root user for security
RUN groupadd --gid 1000 appgroup && \
    useradd --uid 1000 --gid appgroup --shell /bin/bash --create-home appuser

WORKDIR $APP_HOME

# Copy virtual environment from builder
COPY --from=builder /opt/venv /opt/venv

# Copy application files
COPY --chown=appuser:appgroup openapi.json .
COPY --chown=appuser:appgroup powerstore_mcp/ ./powerstore_mcp/

# Create logs directory
RUN mkdir -p /app/logs && chown -R appuser:appgroup /app/logs

# Switch to non-root user
USER appuser

# Expose port
EXPOSE 3000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import httpx; r = httpx.get('http://localhost:3000/health', timeout=5); exit(0 if r.status_code == 200 else 1)"

# Default command: Run HTTP/SSE server
CMD ["python", "-m", "uvicorn", "powerstore_mcp.http_server:app", "--host", "0.0.0.0", "--port", "3000"]

# -----------------------------------------------------------------------------
# Alternative entry points (use with docker run --entrypoint)
# -----------------------------------------------------------------------------
# stdio mode: docker run --rm -i powerstore-mcp python -m powerstore_mcp.main
# http mode:  docker run -p 3000:3000 powerstore-mcp (default)
