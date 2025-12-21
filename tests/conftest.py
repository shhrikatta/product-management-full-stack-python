"""Pytest configuration file (conftest.py).

This file contains pytest configuration and shared fixtures used across all test modules.
It is automatically discovered by pytest and loaded before running tests.

Configuration:
    - Registers custom test markers (unit, integration, slow)
    - Can define shared fixtures accessible to all test modules
    - Can configure pytest hooks and plugins

Custom Markers:
    - @pytest.mark.unit: Marks a test as a unit test
        * Tests individual functions/methods in isolation
        * Fast execution (< 1 second)
        * No external dependencies
        * Use: pytest -m unit
        
    - @pytest.mark.integration: Marks a test as an integration test
        * Tests multiple components together
        * Tests API endpoints with mocked database
        * May involve HTTP requests (via test client)
        * Use: pytest -m integration
        
    - @pytest.mark.slow: Marks a test as slow-running
        * Takes longer than 1 second to execute
        * May involve complex operations
        * Can be excluded with: pytest -m "not slow"

Usage:
    This file is automatically loaded by pytest. No manual import needed.
    All fixtures and configuration defined here are available to all test files.

Note:
    - This file should only contain pytest-specific configuration
    - Test-specific fixtures should be in individual test files
    - Keep this file focused on cross-cutting test concerns

Author: Development Team
Last Updated: December 21, 2025
"""

import pytest


def pytest_configure(config):
    """Configure pytest with custom markers.
    
    This hook is called after command line options have been parsed and all
    plugins and initial conftest files been loaded. Registers custom markers
    to avoid "unknown mark" warnings.
    
    Args:
        config: The pytest config object
        
    Registered Markers:
        - unit: For unit tests (isolated, fast, no external dependencies)
        - integration: For integration tests (multiple components, API tests)
        - slow: For slow-running tests (can be excluded with -m "not slow")
        
    Example Usage in Tests:
        @pytest.mark.unit
        def test_helper_function():
            assert helper() == expected_value
            
        @pytest.mark.integration
        def test_api_endpoint(client):
            response = client.get('/api/products')
            assert response.status_code == 200
    """
    # Register unit test marker
    config.addinivalue_line(
        "markers", "unit: marks tests as unit tests (isolated, fast, no external dependencies)"
    )
    
    # Register integration test marker
    config.addinivalue_line(
        "markers", "integration: marks tests as integration tests (API endpoints, multiple components)"
    )
    
    # Register slow test marker
    config.addinivalue_line(
        "markers", "slow: marks tests as slow-running (can be excluded with -m 'not slow')"
    )
