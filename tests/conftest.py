"""Pytest configuration and fixtures for external tests."""
import os
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

# Prevent main.py from creating tables on import
import sys
from unittest import mock

# Mock the database creation before importing app
with mock.patch('app.db.Base.metadata.create_all'):
    from app.main import app, get_db
    from app.db import Base


# Test database (in-memory SQLite)
TEST_DATABASE_URL = "sqlite:///:memory:"
TEST_API_KEY = "test-api-key-12345"


@pytest.fixture(scope="function")
def test_db_engine():
    """Create a test database engine."""
    engine = create_engine(
        TEST_DATABASE_URL,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(bind=engine)
    yield engine
    Base.metadata.drop_all(bind=engine)
    engine.dispose()


@pytest.fixture(scope="function")
def test_db_session(test_db_engine):
    """Create a test database session."""
    TestingSessionLocal = sessionmaker(
        autocommit=False, autoflush=False, bind=test_db_engine
    )
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()


@pytest.fixture(scope="function")
def client(test_db_session):
    """Create a test client with test database."""
    def override_get_db():
        try:
            yield test_db_session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    
    # Set API key for tests
    os.environ["API_KEY"] = TEST_API_KEY
    
    with TestClient(app) as test_client:
        yield test_client
    
    app.dependency_overrides.clear()


@pytest.fixture
def api_headers():
    """Return headers with API key."""
    return {"X-API-Key": TEST_API_KEY}


@pytest.fixture
def sample_event_payload():
    """Return a sample event payload."""
    return {
        "source": "test-source",
        "payload": {
            "stid": "station-123",
            "exnum": "EX001",
            "table": {
                "column1": "value1",
                "column2": "value2"
            }
        }
    }
