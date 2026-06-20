"""
backend/tests/conftest.py
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

PURPOSE
───────
Shared pytest fixtures for the SolarIQ backend test suite.

Provides a session-scoped TestClient that:
  - Uses TestClient as a context manager to trigger the FastAPI lifespan
  - Calls DataLoader.load() exactly once for the entire pytest session
  - Reuses the same client instance across all test files

Using a session-scoped fixture (rather than function-scoped) mirrors
production behaviour: the CSVs are loaded once at startup and the
in-memory index is shared across all requests.

USAGE
─────
  Tests receive the client via the `client` fixture:

      def test_something(client):
          response = client.get("/health")
          assert response.status_code == 200

  The fixture is available to all test files automatically — no import
  needed in individual test files.
"""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from main import app


@pytest.fixture(scope="session")
def client():
    """
    Session-scoped FastAPI TestClient.

    Enters the TestClient context manager to trigger the FastAPI lifespan
    handler, which calls DataLoader.load() with the real CSV files.
    The same client instance is reused for all tests in the session.
    """
    with TestClient(app) as c:
        yield c
