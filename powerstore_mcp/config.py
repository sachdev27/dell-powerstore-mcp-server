"""Configuration loader for PowerStore MCP Server.

This module provides configuration management using Pydantic models
for validation and environment variable loading.

Example:
    >>> from powerstore_mcp.config import load_config
    >>> config = load_config()
    >>> print(config.server.port)
    3000

Environment Variables:
    POWERSTORE_HOST: Default PowerStore host (optional).
    POWERSTORE_USERNAME: Default username (optional).
    POWERSTORE_PASSWORD: Default password (optional).
    POWERSTORE_API_VERSION: API version (default: v1).
    LOCAL_OPENAPI_SPEC_PATH: Path to OpenAPI spec file (required).
    HTTP_SERVER_PORT: HTTP server port (default: 3000).
    LOG_LEVEL: Logging level (default: INFO).
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import Optional

from dotenv import load_dotenv
from pydantic import BaseModel, Field, field_validator

from .exceptions import ConfigurationError, EnvironmentVariableError
from .logging_config import get_logger

logger = get_logger(__name__)


class PowerStoreConfig(BaseModel):
    """PowerStore connection configuration.

    Attributes:
        host: PowerStore host (optional, can be provided per-request).
        username: PowerStore username (optional).
        password: PowerStore password (optional).
        api_version: PowerStore API version.
        openapi_path: Path to OpenAPI spec on PowerStore.
        local_spec_path: Path to local OpenAPI spec file.
        tls_verify: Whether to verify TLS certificates.
    """

    host: Optional[str] = Field(
        default="localhost",
        description="PowerStore host (optional, provided per-request)",
    )
    username: Optional[str] = Field(
        default=None,
        description="PowerStore username (optional)",
    )
    password: Optional[str] = Field(
        default=None,
        description="PowerStore password (optional)",
    )
    api_version: str = Field(
        default="v1",
        description="PowerStore API version",
    )
    openapi_path: str = Field(
        default="/api/rest/swagger.yaml",
        description="OpenAPI spec path on PowerStore",
    )
    local_spec_path: Optional[str] = Field(
        default=None,
        description="Local OpenAPI spec file path",
    )
    tls_verify: bool = Field(
        default=False,
        description="Verify TLS certificates",
    )

    @field_validator("local_spec_path")
    @classmethod
    def validate_spec_path(cls, v: Optional[str]) -> Optional[str]:
        """Validate that the OpenAPI spec path exists if provided.

        Args:
            v: The path value to validate.

        Returns:
            The validated path.

        Raises:
            ValueError: If the path doesn't exist.
        """
        if v is not None and not Path(v).exists():
            raise ValueError(f"OpenAPI spec file not found: {v}")
        return v

    model_config = {"extra": "ignore"}


class ServerConfig(BaseModel):
    """Server configuration.

    Attributes:
        port: HTTP server port.
        log_level: Logging level.
        log_json: Use JSON format for logs.
        log_file: Optional log file path.
        enable_endpoint_aggregation: Enable aggregated endpoints.
        cache_openapi_spec: Cache OpenAPI spec.
        openapi_cache_ttl: OpenAPI cache TTL in seconds.
        max_retries: Max API retry attempts.
        retry_delay: Retry delay in milliseconds.
        request_timeout: Request timeout in milliseconds.
    """

    port: int = Field(
        default=3000,
        ge=1,
        le=65535,
        description="HTTP server port",
    )
    log_level: str = Field(
        default="INFO",
        description="Logging level",
    )
    log_json: bool = Field(
        default=False,
        description="Use JSON format for logs",
    )
    log_file: Optional[str] = Field(
        default=None,
        description="Optional log file path",
    )
    enable_endpoint_aggregation: bool = Field(
        default=True,
        description="Enable aggregated endpoints",
    )
    cache_openapi_spec: bool = Field(
        default=True,
        description="Cache OpenAPI spec",
    )
    openapi_cache_ttl: int = Field(
        default=3600,
        ge=0,
        description="OpenAPI cache TTL in seconds",
    )
    max_retries: int = Field(
        default=3,
        ge=0,
        le=10,
        description="Max API retry attempts",
    )
    retry_delay: int = Field(
        default=1000,
        ge=0,
        description="Retry delay in milliseconds",
    )
    request_timeout: int = Field(
        default=30000,
        ge=1000,
        description="Request timeout in milliseconds",
    )

    @field_validator("log_level")
    @classmethod
    def validate_log_level(cls, v: str) -> str:
        """Validate log level.

        Args:
            v: The log level to validate.

        Returns:
            The validated log level in uppercase.

        Raises:
            ValueError: If the log level is invalid.
        """
        valid_levels = {"DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"}
        v_upper = v.upper()
        if v_upper not in valid_levels:
            raise ValueError(f"Invalid log level: {v}. Must be one of {valid_levels}")
        return v_upper

    model_config = {"extra": "ignore"}


class Config(BaseModel):
    """Main configuration container.

    Attributes:
        powerstore: PowerStore connection configuration.
        server: Server configuration.
    """

    powerstore: PowerStoreConfig
    server: ServerConfig

    model_config = {"extra": "ignore"}


def load_config(env_file: Optional[Path] = None) -> Config:
    """Load configuration from environment variables.

    Args:
        env_file: Optional path to .env file. If not provided,
                  searches for .env in the current directory.

    Returns:
        Validated configuration object.

    Raises:
        ConfigurationError: If configuration is invalid.
        EnvironmentVariableError: If required environment variable is missing.

    Example:
        >>> config = load_config()
        >>> print(config.server.port)
        3000
    """
    # Load environment variables from .env file
    if env_file:
        load_dotenv(env_file)
    else:
        load_dotenv()

    try:
        # Get spec path, treating empty string as None
        spec_path_value = os.getenv("LOCAL_OPENAPI_SPEC_PATH") or None

        powerstore_config = PowerStoreConfig(
            host=os.getenv("POWERSTORE_HOST", "localhost"),
            username=os.getenv("POWERSTORE_USERNAME"),
            password=os.getenv("POWERSTORE_PASSWORD"),
            api_version=os.getenv("POWERSTORE_API_VERSION", "v1"),
            openapi_path=os.getenv("POWERSTORE_OPENAPI_PATH", "/api/rest/swagger.yaml"),
            local_spec_path=spec_path_value,
            tls_verify=os.getenv("NODE_TLS_REJECT_UNAUTHORIZED", "0") != "0",
        )
    except ValueError as e:
        raise ConfigurationError(f"Invalid PowerStore configuration: {e}") from e

    try:
        server_config = ServerConfig(
            port=int(os.getenv("HTTP_SERVER_PORT", "3000")),
            log_level=os.getenv("LOG_LEVEL", "INFO"),
            log_json=os.getenv("LOG_JSON", "false").lower() == "true",
            log_file=os.getenv("LOG_FILE"),
            enable_endpoint_aggregation=os.getenv("ENABLE_ENDPOINT_AGGREGATION", "true").lower() == "true",
            cache_openapi_spec=os.getenv("CACHE_OPENAPI_SPEC", "true").lower() == "true",
            openapi_cache_ttl=int(os.getenv("OPENAPI_CACHE_TTL", "3600")),
            max_retries=int(os.getenv("MAX_RETRIES", "3")),
            retry_delay=int(os.getenv("RETRY_DELAY", "1000")),
            request_timeout=int(os.getenv("REQUEST_TIMEOUT", "30000")),
        )
    except ValueError as e:
        raise ConfigurationError(f"Invalid server configuration: {e}") from e

    config = Config(powerstore=powerstore_config, server=server_config)

    # Check required configuration
    if not powerstore_config.local_spec_path:
        raise EnvironmentVariableError(
            "LOCAL_OPENAPI_SPEC_PATH",
            "OpenAPI specification path is required for tool generation",
        )

    # Log configuration summary
    if powerstore_config.username and powerstore_config.password:
        logger.info(
            "Configuration loaded: Default credentials available",
            extra={
                "mode": "with_defaults",
                "host": powerstore_config.host,
            },
        )
    else:
        logger.info(
            "Configuration loaded: Credential-free mode",
            extra={"mode": "credential_free"},
        )

    logger.debug(
        "Server configuration",
        extra={
            "port": server_config.port,
            "log_level": server_config.log_level,
            "timeout_ms": server_config.request_timeout,
        },
    )

    return config
