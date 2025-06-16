"""
Pytest configuration file for the API test suite.
This file contains fixtures and configuration that can be reused across test files.
"""
import pytest
import sys
import os

# Add the parent directory to the Python path to allow importing from app
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Define fixtures that can be reused across tests
@pytest.fixture
def test_app():
    """
    Create a test version of the FastAPI app
    """
    from app.main import app
    return app

@pytest.fixture
def client(test_app):
    """
    Create a test client for the FastAPI app
    """
    from fastapi.testclient import TestClient
    return TestClient(test_app)
