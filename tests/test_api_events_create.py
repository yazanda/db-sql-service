"""Tests for event creation endpoint."""
import pytest


def test_create_event_success(client, api_headers, sample_event_payload):
    """Test successful event creation."""
    response = client.post("/v1/events", json=sample_event_payload, headers=api_headers)
    
    assert response.status_code == 200
    data = response.json()
    assert "id" in data
    assert data["id"] > 0
    assert "received_at" in data
    assert data["source"] == sample_event_payload["source"]
    assert data["payload"] == sample_event_payload["payload"]


def test_create_event_without_source(client, api_headers):
    """Test creating an event without source field (optional)."""
    payload = {
        "payload": {
            "stid": "station-456",
            "exnum": "EX002",
            "table": {"col1": "val1"}
        }
    }
    response = client.post("/v1/events", json=payload, headers=api_headers)
    
    assert response.status_code == 200
    data = response.json()
    assert data["source"] is None
    assert data["payload"] == payload["payload"]


def test_create_event_missing_stid(client, api_headers):
    """Test creating an event without required 'stid' in payload."""
    payload = {
        "source": "test",
        "payload": {
            "exnum": "EX003",
            "table": {}
        }
    }
    response = client.post("/v1/events", json=payload, headers=api_headers)
    
    assert response.status_code == 422
    assert "stid" in response.json()["detail"]


def test_create_event_missing_exnum(client, api_headers):
    """Test creating an event without required 'exnum' in payload."""
    payload = {
        "source": "test",
        "payload": {
            "stid": "station-789",
            "table": {}
        }
    }
    response = client.post("/v1/events", json=payload, headers=api_headers)
    
    assert response.status_code == 422
    assert "exnum" in response.json()["detail"]


def test_create_event_missing_table(client, api_headers):
    """Test creating an event without required 'table' in payload."""
    payload = {
        "source": "test",
        "payload": {
            "stid": "station-111",
            "exnum": "EX004"
        }
    }
    response = client.post("/v1/events", json=payload, headers=api_headers)
    
    assert response.status_code == 422
    assert "table" in response.json()["detail"]


def test_create_event_payload_not_dict(client, api_headers):
    """Test creating an event with non-dict payload."""
    payload = {
        "source": "test",
        "payload": "not-a-dict"
    }
    response = client.post("/v1/events", json=payload, headers=api_headers)
    
    assert response.status_code == 422  # Pydantic validation error
    assert "detail" in response.json()


def test_create_event_with_additional_fields(client, api_headers):
    """Test creating an event with additional fields in payload."""
    payload = {
        "source": "test-source",
        "payload": {
            "stid": "station-222",
            "exnum": "EX005",
            "table": {"data": "value"},
            "extra_field": "extra_value",
            "another_field": 12345
        }
    }
    response = client.post("/v1/events", json=payload, headers=api_headers)
    
    assert response.status_code == 200
    data = response.json()
    assert data["payload"]["extra_field"] == "extra_value"
    assert data["payload"]["another_field"] == 12345


def test_create_multiple_events(client, api_headers):
    """Test creating multiple events."""
    events = []
    
    for i in range(5):
        payload = {
            "source": f"source-{i}",
            "payload": {
                "stid": f"station-{i}",
                "exnum": f"EX{i:03d}",
                "table": {"index": i}
            }
        }
        response = client.post("/v1/events", json=payload, headers=api_headers)
        assert response.status_code == 200
        events.append(response.json())
    
    # Verify all events have unique IDs
    ids = [e["id"] for e in events]
    assert len(set(ids)) == 5
    assert all(i > 0 for i in ids)
