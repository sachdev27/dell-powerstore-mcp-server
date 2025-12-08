"""Pytest configuration and shared fixtures.

This module provides common fixtures used across all test modules.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Generator
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

# Sample OpenAPI spec for testing
SAMPLE_OPENAPI_SPEC: dict[str, Any] = {
    "swagger": "2.0",
    "info": {
        "title": "Test PowerStore API",
        "version": "1.0.0",
    },
    "host": "powerstore.example.com",
    "basePath": "/api/rest",
    "paths": {
        "/alert": {
            "get": {
                "operationId": "getAlert",
                "summary": "Get all alerts",
                "parameters": [
                    {
                        "name": "state",
                        "in": "query",
                        "type": "string",
                        "description": "Filter by state",
                    }
                ],
                "responses": {
                    "200": {
                        "description": "Success",
                    }
                },
            }
        },
        "/alert/{id}": {
            "get": {
                "operationId": "getAlertById",
                "summary": "Get alert by ID",
                "parameters": [
                    {
                        "name": "id",
                        "in": "path",
                        "type": "string",
                        "required": True,
                        "description": "Alert ID",
                    }
                ],
                "responses": {
                    "200": {
                        "description": "Success",
                    }
                },
            }
        },
        "/volume": {
            "get": {
                "summary": "Get all volumes",
                "responses": {
                    "200": {
                        "description": "Success",
                    }
                },
            }
        },
        "/appliance": {
            "get": {
                "operationId": "getAppliance",
                "summary": "Get all appliances",
                "responses": {
                    "200": {
                        "description": "Success",
                    }
                },
            }
        },
    },
    "definitions": {
        "alert_instance": {
            "type": "object",
            "properties": {
                "id": {"type": "string", "description": "Unique identifier"},
                "name": {"type": "string", "description": "Alert name"},
                "state": {"type": "string", "description": "Alert state"},
                "severity": {"type": "string", "description": "Alert severity"},
                "description": {"type": "string", "description": "Alert description"},
            },
        },
        "volume_instance": {
            "type": "object",
            "properties": {
                "id": {"type": "string", "description": "Unique identifier"},
                "name": {"type": "string", "description": "Volume name"},
                "size": {"type": "integer", "description": "Volume size"},
            },
        },
    },
}


@pytest.fixture
def sample_openapi_spec() -> dict[str, Any]:
    """Provide a sample OpenAPI specification for testing.

    Returns:
        A minimal OpenAPI spec dictionary.
    """
    return SAMPLE_OPENAPI_SPEC.copy()


@pytest.fixture
def temp_openapi_file(tmp_path: Path, sample_openapi_spec: dict[str, Any]) -> Path:
    """Create a temporary OpenAPI spec file.

    Args:
        tmp_path: Pytest temporary path fixture.
        sample_openapi_spec: Sample OpenAPI spec fixture.

    Returns:
        Path to the temporary OpenAPI spec file.
    """
    spec_file = tmp_path / "openapi.json"
    spec_file.write_text(json.dumps(sample_openapi_spec))
    return spec_file


@pytest.fixture
def mock_env_vars(temp_openapi_file: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Set up mock environment variables for testing.

    Args:
        temp_openapi_file: Temporary OpenAPI spec file fixture.
        monkeypatch: Pytest monkeypatch fixture.
    """
    monkeypatch.setenv("LOCAL_OPENAPI_SPEC_PATH", str(temp_openapi_file))
    monkeypatch.setenv("LOG_LEVEL", "DEBUG")
    monkeypatch.setenv("HTTP_SERVER_PORT", "3001")


@pytest.fixture
def sample_alert_response() -> list[dict[str, Any]]:
    """Provide a sample alert API response.

    Returns:
        List of sample alert dictionaries.
    """
    return [
        {
            "id": "alert-001",
            "name": "Test Alert 1",
            "state": "ACTIVE",
            "severity": "Critical",
            "description": "Test critical alert",
        },
        {
            "id": "alert-002",
            "name": "Test Alert 2",
            "state": "ACTIVE",
            "severity": "Info",
            "description": "Test info alert",
        },
    ]


@pytest.fixture
def sample_volume_response() -> list[dict[str, Any]]:
    """Provide a sample volume API response.

    Returns:
        List of sample volume dictionaries.
    """
    return [
        {
            "id": "vol-001",
            "name": "production-data",
            "size": 1073741824,
        },
        {
            "id": "vol-002",
            "name": "backup-storage",
            "size": 2147483648,
        },
    ]


@pytest.fixture
def mock_httpx_client(sample_alert_response: list[dict[str, Any]]) -> Generator[MagicMock, None, None]:
    """Create a mock httpx client.

    Args:
        sample_alert_response: Sample alert data fixture.

    Yields:
        Mock httpx.AsyncClient instance.
    """
    with patch("httpx.AsyncClient") as mock_client_class:
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.content = b'{"data": []}'
        mock_response.json.return_value = sample_alert_response
        mock_response.raise_for_status = MagicMock()

        mock_client.request = AsyncMock(return_value=mock_response)
        mock_client.aclose = AsyncMock()
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock()

        mock_client_class.return_value = mock_client
        yield mock_client


# Configure pytest-asyncio
pytest_plugins = ("pytest_asyncio",)
