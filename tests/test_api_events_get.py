"""Tests for getting specific events endpoint."""
import pytest


def test_get_event_success(client, api_headers, sample_event_payload):
    """Test successfully getting an event by ID and exnum."""
    # Create an event
    create_response = client.post("/v1/events", json=sample_event_payload, headers=api_headers)
    created_event = create_response.json()
    event_id = created_event["id"]
    exnum = sample_event_payload["payload"]["exnum"]
    
    # Get the event
    response = client.get(f"/v1/events/{event_id}?exnum={exnum}", headers=api_headers)
    
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == event_id
    assert data["source"] == sample_event_payload["source"]
    assert data["payload"] == sample_event_payload["payload"]


def test_get_event_not_found(client, api_headers):
    """Test getting a non-existent event."""
    response = client.get("/v1/events/99999?exnum=EX001", headers=api_headers)
    
    assert response.status_code == 404
    assert "Not found" in response.json()["detail"]


def test_get_event_wrong_exnum(client, api_headers, sample_event_payload):
    """Test getting an event with wrong exnum returns 404."""
    # Create an event
    create_response = client.post("/v1/events", json=sample_event_payload, headers=api_headers)
    created_event = create_response.json()
    event_id = created_event["id"]
    
    # Try to get with wrong exnum
    response = client.get(f"/v1/events/{event_id}?exnum=WRONG", headers=api_headers)
    
    assert response.status_code == 404
    assert "Not found" in response.json()["detail"]


def test_get_event_missing_exnum(client, api_headers, sample_event_payload):
    """Test getting an event without exnum parameter."""
    # Create an event
    create_response = client.post("/v1/events", json=sample_event_payload, headers=api_headers)
    created_event = create_response.json()
    event_id = created_event["id"]
    
    # Try to get without exnum
    response = client.get(f"/v1/events/{event_id}", headers=api_headers)
    
    assert response.status_code == 422  # Validation error


def test_get_event_empty_exnum(client, api_headers, sample_event_payload):
    """Test getting an event with empty exnum."""
    # Create an event
    create_response = client.post("/v1/events", json=sample_event_payload, headers=api_headers)
    created_event = create_response.json()
    event_id = created_event["id"]
    
    # Try to get with empty exnum
    response = client.get(f"/v1/events/{event_id}?exnum=", headers=api_headers)
    
    assert response.status_code == 422  # Validation error


def test_get_multiple_events_individually(client, api_headers):
    """Test getting multiple events by their IDs."""
    # Create multiple events with different exnums
    created_events = []
    for i in range(3):
        payload = {
            "source": f"source-{i}",
            "payload": {
                "stid": f"station-{i}",
                "exnum": f"EX{i:03d}",
                "table": {"index": i}
            }
        }
        response = client.post("/v1/events", json=payload, headers=api_headers)
        created_events.append(response.json())
    
    # Get each event individually
    for created in created_events:
        event_id = created["id"]
        exnum = created["payload"]["exnum"]
        
        response = client.get(f"/v1/events/{event_id}?exnum={exnum}", headers=api_headers)
        assert response.status_code == 200
        
        data = response.json()
        assert data["id"] == event_id
        assert data["payload"]["exnum"] == exnum


def test_get_event_cross_exnum_isolation(client, api_headers):
    """Test that events with different exnums are isolated."""
    # Create two events with different exnums
    payload1 = {
        "payload": {
            "stid": "station-1",
            "exnum": "EX001",
            "table": {}
        }
    }
    payload2 = {
        "payload": {
            "stid": "station-2",
            "exnum": "EX002",
            "table": {}
        }
    }
    
    response1 = client.post("/v1/events", json=payload1, headers=api_headers)
    response2 = client.post("/v1/events", json=payload2, headers=api_headers)
    
    event1_id = response1.json()["id"]
    event2_id = response2.json()["id"]
    
    # Try to get event1 with event2's exnum
    response = client.get(f"/v1/events/{event1_id}?exnum=EX002", headers=api_headers)
    assert response.status_code == 404
    
    # Try to get event2 with event1's exnum
    response = client.get(f"/v1/events/{event2_id}?exnum=EX001", headers=api_headers)
    assert response.status_code == 404
    
    # Verify correct access
    response = client.get(f"/v1/events/{event1_id}?exnum=EX001", headers=api_headers)
    assert response.status_code == 200
    
    response = client.get(f"/v1/events/{event2_id}?exnum=EX002", headers=api_headers)
    assert response.status_code == 200
