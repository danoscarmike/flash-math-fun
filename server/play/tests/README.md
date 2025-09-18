# Tests Directory

This directory contains all tests for the Flash Card Magic application.

## Structure

```
tests/
├── conftest.py              # Test configuration and fixtures
├── test_services.py         # Unit tests for services module
├── test_components.py       # Component tests for UI elements
├── test_integration.py      # Integration tests for workflows
├── test_pages.py           # Page-level tests
└── README.md               # This file
```

## Quick Start

```bash
# Run all tests
python -m pytest

# Run with coverage
python -m pytest --cov=app

# Run specific test type
python -m pytest -m unit
```

## Test Categories

- **Unit Tests**: Test individual functions and classes
- **Component Tests**: Test UI components with mocks
- **Integration Tests**: Test complete workflows
- **Page Tests**: Test page-level functionality

See [TESTING.md](../TESTING.md) for detailed documentation.
