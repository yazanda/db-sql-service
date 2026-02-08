# Tests

This directory contains external/integration tests for the db-sql-service API.

## Structure

- `conftest.py` - Pytest configuration and shared fixtures
- `test_api_health.py` - Health check endpoint tests
- `test_api_authentication.py` - Authentication and API key tests
- `test_api_events_create.py` - Event creation endpoint tests
- `test_api_events_list.py` - Event listing endpoint tests
- `test_api_events_get.py` - Event retrieval endpoint tests
- `test_integration_workflow.py` - End-to-end workflow tests
- `pytest.ini` - Pytest configuration

## Running Tests

### Install dependencies first:
```bash
pip install -r requirments.txt
pip install pytest pytest-cov httpx
```

### Run all tests:
```bash
pytest
```

### Run with coverage:
```bash
pytest --cov=app --cov-report=html
```

### Run specific test file:
```bash
pytest tests/test_api_events_create.py
```

### Run specific test:
```bash
pytest tests/test_api_events_create.py::test_create_event_success
```

### Run with verbose output:
```bash
pytest -v
```

### Run only integration tests:
```bash
pytest -m integration
```

## Test Coverage

The test suite covers:
- ✅ Health check endpoint
- ✅ API authentication and authorization
- ✅ Event creation with validation
- ✅ Event listing with pagination
- ✅ Event retrieval with exnum matching
- ✅ Error handling and edge cases
- ✅ Complete CRUD workflows
- ✅ Multi-source scenarios
- ✅ High-volume operations

## Fixtures

### `client`
A FastAPI TestClient instance with test database configured.

### `api_headers`
Headers with valid API key for authenticated requests.

### `sample_event_payload`
A sample valid event payload for testing.

### `test_db_session`
An in-memory SQLite database session for isolated testing.

## Notes

- Tests use an in-memory SQLite database for isolation
- Each test function gets a fresh database
- API key is set to `test-api-key-12345` for tests
- Tests are independent and can run in any order
