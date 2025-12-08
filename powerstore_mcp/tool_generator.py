"""OpenAPI tool generator for PowerStore MCP Server.

This module parses OpenAPI specifications and generates MCP tool definitions
with enhanced descriptions for LLM context.

Example:
    >>> from powerstore_mcp.tool_generator import ToolGenerator, load_openapi_spec
    >>> spec = load_openapi_spec("openapi.json")
    >>> generator = ToolGenerator(spec)
    >>> tools = generator.generate_tools()
    >>> print(f"Generated {len(tools)} tools")

Note:
    Only GET methods are generated for safe read-only operations.
    Each tool includes credential parameters (host, username, password)
    that must be provided per-request.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Optional

import yaml

from .exceptions import OpenAPILoadError, OpenAPIParseError
from .logging_config import get_logger

logger = get_logger(__name__)

# Maximum number of fields to show in description
MAX_FIELDS_DISPLAY = 20
MAX_KEY_FIELDS = 10
MAX_ENUM_VALUES = 5


class ToolGenerator:
    """Generate MCP tools from OpenAPI specification.

    This class parses an OpenAPI 2.0/3.0 specification and generates
    MCP tool definitions for each GET endpoint. Tools include enhanced
    descriptions with schema information for better LLM understanding.

    Attributes:
        spec: The parsed OpenAPI specification.
        tool_names: Dictionary tracking tool name usage for uniqueness.

    Example:
        >>> generator = ToolGenerator(spec)
        >>> tools = generator.generate_tools()
        >>> for tool in tools:
        ...     print(f"{tool['name']}: {tool['description'][:50]}...")
    """

    def __init__(self, spec: dict[str, Any]) -> None:
        """Initialize tool generator with OpenAPI spec.

        Args:
            spec: Parsed OpenAPI specification dictionary.
        """
        self.spec = spec
        self.tool_names: dict[str, int] = {}

    def generate_tools(self) -> list[dict[str, Any]]:
        """Generate all MCP tools from OpenAPI spec (GET methods only).

        Returns:
            List of MCP tool definitions.

        Note:
            Only GET methods are included for safe read-only operations.
        """
        tools: list[dict[str, Any]] = []
        paths = self.spec.get("paths", {})

        for path, path_item in paths.items():
            # Only generate tools for GET methods (read-only for diagnosis)
            if "get" in path_item:
                operation = path_item["get"]
                tool = self._generate_tool_from_operation(path, "get", operation)
                if tool:
                    tools.append(tool)

        logger.info(
            "Generated MCP tools from OpenAPI spec",
            extra={"tool_count": len(tools), "methods": ["GET"]},
        )
        return tools

    def _generate_tool_from_operation(
        self,
        path: str,
        method: str,
        operation: dict[str, Any],
    ) -> Optional[dict[str, Any]]:
        """Generate a single MCP tool from an OpenAPI operation.

        Args:
            path: API endpoint path (e.g., "/volume", "/alert/{id}").
            method: HTTP method (lowercase).
            operation: OpenAPI operation object.

        Returns:
            MCP tool definition or None if generation fails.
        """
        try:
            # Generate tool name from operationId or path + method
            tool_name = operation.get("operationId") or self._generate_tool_name_from_path(
                path, method
            )

            # Make tool name unique if duplicate exists
            tool_name = self._make_unique_name(tool_name, path)

            # Generate base description
            base_description = (
                operation.get("summary")
                or operation.get("description")
                or f"{method.upper()} {path}"
            )

            # Detect if this is a collection query (no {id} in path)
            is_collection_query = "{id}" not in path

            # Get resource name from path (e.g., /alert -> alert)
            resource_name = self._get_resource_name_from_path(path)

            # Build enhanced description with schema info
            description = self._build_enhanced_description(
                base_description, resource_name, is_collection_query
            )

            # Generate input schema from parameters
            input_schema = self._generate_input_schema(operation, is_collection_query)

            return {
                "name": tool_name,
                "description": description,
                "inputSchema": input_schema,
            }

        except Exception as e:
            logger.warning(
                f"Failed to generate tool for {method.upper()} {path}",
                extra={"error": str(e), "path": path, "method": method},
            )
            return None

    def _get_resource_name_from_path(self, path: str) -> str:
        """Extract resource name from API path.

        Args:
            path: API endpoint path (e.g., "/alert", "/volume/{id}").

        Returns:
            Resource name (e.g., "alert", "volume").
        """
        parts = [p for p in path.split("/") if p and not p.startswith("{")]
        return parts[0] if parts else ""

    def _build_enhanced_description(
        self,
        base_description: str,
        resource_name: str,
        is_collection_query: bool,
    ) -> str:
        """Build enhanced description with schema info for LLM context.

        Args:
            base_description: Original operation description.
            resource_name: Name of the resource (e.g., "alert", "volume").
            is_collection_query: Whether this is a collection query.

        Returns:
            Enhanced description with available fields and filter info.
        """
        description = base_description

        # Try to find schema definition for this resource
        definitions = self.spec.get("definitions", {})
        instance_def = definitions.get(f"{resource_name}_instance", {})
        properties = instance_def.get("properties", {})

        if properties and is_collection_query:
            # Add available fields for 'select' parameter
            field_names = sorted(properties.keys())
            fields_summary = ", ".join(field_names[:MAX_FIELDS_DISPLAY])
            if len(field_names) > MAX_FIELDS_DISPLAY:
                fields_summary += f", ... ({len(field_names)} total fields)"

            description += f"\n\nAvailable fields for 'select': {fields_summary}"

            # Add key fields with descriptions for common use cases
            key_fields = self._get_key_fields(properties, resource_name)
            if key_fields:
                description += f"\n\nKey fields:\n{key_fields}"

            # Add filter examples based on resource type
            filter_examples = self._get_filter_examples(resource_name, properties)
            if filter_examples:
                description += f"\n\nFilter examples (queryParams):\n{filter_examples}"

        return description

    def _get_key_fields(
        self, properties: dict[str, Any], resource_name: str
    ) -> str:
        """Get formatted list of key fields with descriptions.

        Args:
            properties: Schema properties dict.
            resource_name: Name of the resource.

        Returns:
            Formatted string of key fields.
        """
        # Priority fields that are commonly useful
        priority_fields = [
            "id",
            "name",
            "state",
            "status",
            "severity",
            "type",
            "description",
            "description_l10n",
            "is_acknowledged",
            "resource_name",
            "resource_type",
            "generated_timestamp",
            "created_timestamp",
            "size",
            "logical_used",
        ]

        lines: list[str] = []
        for field in priority_fields:
            if field in properties:
                prop = properties[field]
                desc = prop.get("description", "")[:80]
                enum = prop.get("enum")
                enum_ref = prop.get("$ref", "")

                field_info = f"- {field}"
                if desc:
                    field_info += f": {desc}"
                if enum:
                    enum_str = ", ".join(str(e) for e in enum[:MAX_ENUM_VALUES])
                    field_info += f" (values: {enum_str})"
                elif "Enum" in enum_ref:
                    # Extract enum name from $ref
                    enum_name = enum_ref.split("/")[-1]
                    enum_def = self.spec.get("definitions", {}).get(enum_name, {})
                    enum_values = enum_def.get("enum", [])
                    if enum_values:
                        enum_str = ", ".join(
                            str(e) for e in enum_values[:MAX_ENUM_VALUES]
                        )
                        field_info += f" (values: {enum_str})"

                lines.append(field_info)

        return "\n".join(lines[:MAX_KEY_FIELDS])

    def _get_filter_examples(
        self, resource_name: str, properties: dict[str, Any]
    ) -> str:
        """Generate filter examples based on resource type.

        Args:
            resource_name: Name of the resource.
            properties: Schema properties.

        Returns:
            Filter examples string.
        """
        examples: list[str] = []

        # Resource-specific filter examples
        if resource_name == "alert":
            examples = [
                '{"state": "eq.ACTIVE"} - Active alerts only',
                '{"severity": "eq.Critical"} - Critical severity only',
                '{"is_acknowledged": "eq.false"} - Unacknowledged alerts',
                '{"state": "eq.ACTIVE", "severity": "eq.Critical", '
                '"is_acknowledged": "eq.false"} - Active critical unacknowledged',
            ]
        elif resource_name == "volume":
            examples = [
                '{"state": "eq.Ready"} - Ready volumes only',
                '{"type": "neq.Snapshot"} - Exclude snapshots',
            ]
        elif resource_name == "appliance":
            examples = ['{"is_valid": "eq.true"} - Valid appliances only']
        elif "state" in properties:
            examples = ['{"state": "eq.<value>"} - Filter by state']

        return "\n".join(f"- {ex}" for ex in examples) if examples else ""

    def _make_unique_name(self, tool_name: str, path: str) -> str:
        """Make tool name unique by adding suffix if needed.

        Args:
            tool_name: Original tool name.
            path: API path for generating suffix.

        Returns:
            Unique tool name.
        """
        if tool_name in self.tool_names:
            count = self.tool_names[tool_name] + 1
            self.tool_names[tool_name] = count

            # Add path-based suffix to make it unique
            path_parts = [p for p in path.split("/") if p and not p.startswith("{")]
            path_suffix = "_".join(path_parts) if path_parts else str(count)
            tool_name = f"{tool_name}_{path_suffix}"
        else:
            self.tool_names[tool_name] = 0

        return tool_name

    def _generate_tool_name_from_path(self, path: str, method: str) -> str:
        """Generate tool name from path and method.

        Args:
            path: API endpoint path.
            method: HTTP method.

        Returns:
            Generated tool name in camelCase.
        """
        # Remove leading slash and filter out path parameters
        path_parts = [p for p in path.split("/") if p and not p.startswith("{")]

        # Combine method and path parts
        parts = [method] + path_parts

        # Convert to camelCase
        name = ""
        for i, part in enumerate(parts):
            # Clean non-alphanumeric characters
            cleaned = "".join(c if c.isalnum() else "_" for c in part)

            if i == 0:
                name = cleaned.lower()
            else:
                name += cleaned.capitalize()

        return name

    def _generate_input_schema(
        self, operation: dict[str, Any], is_collection_query: bool = False
    ) -> dict[str, Any]:
        """Generate input schema from operation parameters.

        Args:
            operation: OpenAPI operation object.
            is_collection_query: Whether this is a collection query.

        Returns:
            JSON Schema for tool input.
        """
        properties: dict[str, Any] = {
            "host": {
                "type": "string",
                "description": "PowerStore host (e.g., powerstore.example.com)",
            },
            "username": {
                "type": "string",
                "description": "PowerStore username",
            },
            "password": {
                "type": "string",
                "description": "PowerStore password",
            },
        }
        required = ["host", "username", "password"]

        # Add parameters from OpenAPI spec
        parameters = operation.get("parameters", [])
        for param in parameters:
            param_name = param.get("name")
            if not param_name:
                continue

            param_in = param.get("in")
            if param_in not in ["query", "path"]:
                continue

            # Build parameter schema
            param_schema: dict[str, Any] = {
                "type": self._convert_openapi_type(param.get("type", "string")),
                "description": param.get("description", ""),
            }

            # Add enum if present
            if "enum" in param:
                param_schema["enum"] = param["enum"]

            properties[param_name] = param_schema

            # Add to required if parameter is required
            if param.get("required", False):
                required.append(param_name)

        # Add PowerStore standard query parameters for collection queries
        if is_collection_query:
            properties["select"] = {
                "type": "string",
                "description": "Comma-separated list of field names to return (e.g., 'id,name,state')",
            }
            properties["limit"] = {
                "type": "integer",
                "description": "Maximum number of results to return",
            }
            properties["offset"] = {
                "type": "integer",
                "description": "Number of results to skip (for pagination)",
            }
            properties["queryParams"] = {
                "type": "object",
                "description": (
                    "Additional query filters "
                    "(e.g., {'state': 'eq.ACTIVE', 'severity': 'eq.Critical'})"
                ),
                "additionalProperties": {"type": "string"},
            }

        return {
            "type": "object",
            "properties": properties,
            "required": required,
            "additionalProperties": False,
        }

    def _convert_openapi_type(self, openapi_type: str) -> str:
        """Convert OpenAPI type to JSON Schema type.

        Args:
            openapi_type: OpenAPI type string.

        Returns:
            JSON Schema type string.
        """
        type_mapping = {
            "integer": "number",
            "number": "number",
            "string": "string",
            "boolean": "boolean",
            "array": "array",
            "object": "object",
        }
        return type_mapping.get(openapi_type, "string")


def load_openapi_spec(file_path: str) -> dict[str, Any]:
    """Load OpenAPI specification from file.

    Supports both JSON and YAML formats. The format is determined
    by the file extension.

    Args:
        file_path: Path to OpenAPI spec file (JSON or YAML).

    Returns:
        Parsed OpenAPI specification.

    Raises:
        OpenAPILoadError: If file doesn't exist or cannot be read.
        OpenAPIParseError: If file format is invalid.

    Example:
        >>> spec = load_openapi_spec("openapi.json")
        >>> print(spec["info"]["title"])
        "Dell PowerStore REST API"
    """
    path = Path(file_path)

    if not path.exists():
        raise OpenAPILoadError(file_path, message=f"OpenAPI spec file not found: {file_path}")

    try:
        with open(path, "r", encoding="utf-8") as f:
            if path.suffix in [".yaml", ".yml"]:
                return yaml.safe_load(f)
            elif path.suffix == ".json":
                return json.load(f)
            else:
                # Try JSON first, then YAML
                content = f.read()
                try:
                    return json.loads(content)
                except json.JSONDecodeError:
                    return yaml.safe_load(content)
    except (json.JSONDecodeError, yaml.YAMLError) as e:
        raise OpenAPIParseError(file_path, e) from e
    except OSError as e:
        raise OpenAPILoadError(file_path, e) from e
