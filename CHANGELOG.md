# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Initial Python implementation of Dell PowerStore MCP Server
- Automatic tool generation from OpenAPI specification (262 tools)
- Credential-free architecture with per-request authentication
- HTTP/SSE transport for n8n and web clients
- stdio transport for Claude Desktop
- Comprehensive logging with structured JSON output
- Custom exception hierarchy for better error handling
- Health check endpoint with detailed metrics
- Type hints throughout the codebase
- Unit test suite with pytest
- GitHub Actions CI/CD pipeline
- Pre-commit hooks for code quality
- Docker support with multi-stage builds

### Security
- Per-request Basic authentication (no stored credentials)
- TLS certificate verification (configurable for development)
- No sensitive data in logs

## [1.0.0] - TBD

### Added
- First stable release
- Full Dell PowerStore API support (GET operations)
- Production-ready Docker images
- Comprehensive documentation

---

## Release Notes Template

When creating a new release, copy this template:

```markdown
## [X.Y.Z] - YYYY-MM-DD

### Added
- New features

### Changed
- Changes in existing functionality

### Deprecated
- Soon-to-be removed features

### Removed
- Removed features

### Fixed
- Bug fixes

### Security
- Security improvements
```

[Unreleased]: https://github.com/sachdev27/powerstore-mcp-server/compare/v1.0.0...HEAD
[1.0.0]: https://github.com/sachdev27/powerstore-mcp-server/releases/tag/v1.0.0
