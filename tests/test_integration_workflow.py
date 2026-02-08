"""Integration tests for complete workflows."""
import pytest


def test_complete_crud_workflow(client, api_headers):
    """Test a complete workflow: create, list, get events."""
    # 1. Verify empty state
    response = client.get("/v1/events", headers=api_headers)
    assert response.status_code == 200
    assert len(response.json()) == 0
    
    # 2. Create multiple events
    created_events = []
    for i in range(5):
        payload = {
            "source": f"integration-test-{i}",
            "payload": {
                "stid": f"station-{i}",
                "exnum": f"INT{i:03d}",
                "table": {
                    "timestamp": f"2024-01-{i+1:02d}",
                    "value": i * 10
                }
            }
        }
        response = client.post("/v1/events", json=payload, headers=api_headers)
        assert response.status_code == 200
        created_events.append(response.json())
    
    # 3. List all events
    response = client.get("/v1/events", headers=api_headers)
    assert response.status_code == 200
    events = response.json()
    assert len(events) == 5
    
    # 4. Verify order (descending by ID)
    for i in range(len(events) - 1):
        assert events[i]["id"] > events[i + 1]["id"]
    
    # 5. Get each event individually
    for created in created_events:
        event_id = created["id"]
        exnum = created["payload"]["exnum"]
        
        response = client.get(f"/v1/events/{event_id}?exnum={exnum}", headers=api_headers)
        assert response.status_code == 200
        
        retrieved = response.json()
        assert retrieved["id"] == created["id"]
        assert retrieved["source"] == created["source"]
        assert retrieved["payload"] == created["payload"]
    
    # 6. Test pagination
    response = client.get("/v1/events?limit=2&offset=0", headers=api_headers)
    assert response.status_code == 200
    assert len(response.json()) == 2
    
    response = client.get("/v1/events?limit=2&offset=2", headers=api_headers)
    assert response.status_code == 200
    assert len(response.json()) == 2
    
    response = client.get("/v1/events?limit=2&offset=4", headers=api_headers)
    assert response.status_code == 200
    assert len(response.json()) == 1


def test_multi_source_workflow(client, api_headers):
    """Test workflow with events from multiple sources."""
    sources = ["mobile-app", "web-app", "iot-device", "external-api"]
    
    # Create events from different sources
    for source in sources:
        for i in range(3):
            payload = {
                "source": source,
                "payload": {
                    "stid": f"{source}-station-{i}",
                    "exnum": f"{source}-{i}",
                    "table": {"source_data": f"data-{i}"}
                }
            }
            response = client.post("/v1/events", json=payload, headers=api_headers)
            assert response.status_code == 200
    
    # List all events
    response = client.get("/v1/events?limit=100", headers=api_headers)
    assert response.status_code == 200
    events = response.json()
    assert len(events) == 12  # 4 sources * 3 events
    
    # Verify all sources are present
    event_sources = [e["source"] for e in events]
    for source in sources:
        assert event_sources.count(source) == 3


def test_error_recovery_workflow(client, api_headers):
    """Test workflow with error conditions and recovery."""
    # 1. Try to create invalid event (missing required field)
    invalid_payload = {
        "payload": {
            "stid": "station-1",
            "exnum": "ERR001"
            # Missing 'table' field
        }
    }
    response = client.post("/v1/events", json=invalid_payload, headers=api_headers)
    assert response.status_code == 422
    
    # 2. Create valid event after error
    valid_payload = {
        "payload": {
            "stid": "station-1",
            "exnum": "ERR002",
            "table": {}
        }
    }
    response = client.post("/v1/events", json=valid_payload, headers=api_headers)
    assert response.status_code == 200
    event_id = response.json()["id"]
    
    # 3. Try to get with wrong exnum
    response = client.get(f"/v1/events/{event_id}?exnum=WRONG", headers=api_headers)
    assert response.status_code == 404
    
    # 4. Get with correct exnum
    response = client.get(f"/v1/events/{event_id}?exnum=ERR002", headers=api_headers)
    assert response.status_code == 200
    assert response.json()["id"] == event_id


def test_high_volume_workflow(client, api_headers):
    """Test workflow with higher volume of events."""
    num_events = 50
    
    # Create many events
    for i in range(num_events):
        payload = {
            "source": f"high-volume-{i % 5}",  # 5 different sources
            "payload": {
                "stid": f"station-{i}",
                "exnum": f"HV{i:04d}",
                "table": {
                    "batch": i // 10,
                    "index": i % 10
                }
            }
        }
        response = client.post("/v1/events", json=payload, headers=api_headers)
        assert response.status_code == 200
    
    # List with default pagination
    response = client.get("/v1/events", headers=api_headers)
    assert response.status_code == 200
    events = response.json()
    assert len(events) == 50  # Default limit is 50
    
    # List all events
    response = client.get("/v1/events?limit=100", headers=api_headers)
    assert response.status_code == 200
    events = response.json()
    assert len(events) == num_events
    
    # Verify IDs are unique
    ids = [e["id"] for e in events]
    assert len(set(ids)) == num_events


def test_concurrent_source_simulation(client, api_headers):
    """Simulate concurrent requests from different sources."""
    # This test simulates what would happen with concurrent requests
    # by creating events in an interleaved pattern
    
    events_created = []
    
    for round_num in range(5):
        for source_id in ["A", "B", "C"]:
            payload = {
                "source": f"source-{source_id}",
                "payload": {
                    "stid": f"station-{source_id}-{round_num}",
                    "exnum": f"{source_id}{round_num}",
                    "table": {
                        "round": round_num,
                        "source": source_id
                    }
                }
            }
            response = client.post("/v1/events", json=payload, headers=api_headers)
            assert response.status_code == 200
            events_created.append(response.json())
    
    # Verify all were created
    assert len(events_created) == 15
    
    # List and verify
    response = client.get("/v1/events?limit=20", headers=api_headers)
    assert response.status_code == 200
    events = response.json()
    assert len(events) == 15
    
    # Verify each can be retrieved with correct exnum
    for created in events_created:
        response = client.get(
            f"/v1/events/{created['id']}?exnum={created['payload']['exnum']}",
            headers=api_headers
        )
        assert response.status_code == 200
