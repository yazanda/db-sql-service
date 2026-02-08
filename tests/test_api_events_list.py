"""Tests for listing events endpoint."""
import pytest


def test_list_events_empty(client, api_headers):
    """Test listing events when database is empty."""
    response = client.get("/v1/events", headers=api_headers)
    
    assert response.status_code == 200
    assert response.json() == []


def test_list_events_with_data(client, api_headers):
    """Test listing events after creating some."""
    # Create 3 events
    for i in range(3):
        payload = {
            "source": f"source-{i}",
            "payload": {
                "stid": f"station-{i}",
                "exnum": f"EX{i:03d}",
                "table": {"index": i}
            }
        }
        client.post("/v1/events", json=payload, headers=api_headers)
    
    # List events
    response = client.get("/v1/events", headers=api_headers)
    
    assert response.status_code == 200
    events = response.json()
    assert len(events) == 3
    
    # Verify ordering (descending by ID)
    assert events[0]["id"] > events[1]["id"]
    assert events[1]["id"] > events[2]["id"]


def test_list_events_with_limit(client, api_headers):
    """Test listing events with limit parameter."""
    # Create 10 events
    for i in range(10):
        payload = {
            "payload": {
                "stid": f"station-{i}",
                "exnum": f"EX{i:03d}",
                "table": {}
            }
        }
        client.post("/v1/events", json=payload, headers=api_headers)
    
    # List with limit=5
    response = client.get("/v1/events?limit=5", headers=api_headers)
    
    assert response.status_code == 200
    events = response.json()
    assert len(events) == 5


def test_list_events_with_offset(client, api_headers):
    """Test listing events with offset parameter."""
    # Create 5 events
    created_ids = []
    for i in range(5):
        payload = {
            "payload": {
                "stid": f"station-{i}",
                "exnum": f"EX{i:03d}",
                "table": {}
            }
        }
        response = client.post("/v1/events", json=payload, headers=api_headers)
        created_ids.append(response.json()["id"])
    
    # List with offset=2
    response = client.get("/v1/events?offset=2", headers=api_headers)
    
    assert response.status_code == 200
    events = response.json()
    assert len(events) == 3


def test_list_events_with_limit_and_offset(client, api_headers):
    """Test listing events with both limit and offset."""
    # Create 10 events
    for i in range(10):
        payload = {
            "payload": {
                "stid": f"station-{i}",
                "exnum": f"EX{i:03d}",
                "table": {}
            }
        }
        client.post("/v1/events", json=payload, headers=api_headers)
    
    # List with limit=3 and offset=4
    response = client.get("/v1/events?limit=3&offset=4", headers=api_headers)
    
    assert response.status_code == 200
    events = response.json()
    assert len(events) == 3


def test_list_events_limit_too_high(client, api_headers):
    """Test that limit is capped at maximum."""
    # Create 5 events
    for i in range(5):
        payload = {
            "payload": {
                "stid": f"station-{i}",
                "exnum": f"EX{i:03d}",
                "table": {}
            }
        }
        client.post("/v1/events", json=payload, headers=api_headers)
    
    # Request with very high limit (should be capped at 200)
    response = client.get("/v1/events?limit=1000", headers=api_headers)
    
    assert response.status_code == 200
    events = response.json()
    assert len(events) == 5  # Only 5 events exist


def test_list_events_negative_offset(client, api_headers):
    """Test that negative offset is handled (should be set to 0)."""
    # Create 3 events
    for i in range(3):
        payload = {
            "payload": {
                "stid": f"station-{i}",
                "exnum": f"EX{i:03d}",
                "table": {}
            }
        }
        client.post("/v1/events", json=payload, headers=api_headers)
    
    response = client.get("/v1/events?offset=-5", headers=api_headers)
    
    assert response.status_code == 200
    events = response.json()
    assert len(events) == 3


def test_list_events_structure(client, api_headers, sample_event_payload):
    """Test that listed events have correct structure."""
    # Create one event
    client.post("/v1/events", json=sample_event_payload, headers=api_headers)
    
    # List events
    response = client.get("/v1/events", headers=api_headers)
    
    assert response.status_code == 200
    events = response.json()
    assert len(events) == 1
    
    event = events[0]
    assert "id" in event
    assert "received_at" in event
    assert "source" in event
    assert "payload" in event
    assert event["payload"] == sample_event_payload["payload"]
