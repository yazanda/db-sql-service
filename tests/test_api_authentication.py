"""Tests for API authentication."""
import pytest


def test_create_event_without_api_key(client, sample_event_payload):
    """Test that creating an event without API key returns 401."""
    response = client.post("/v1/events", json=sample_event_payload)
    assert response.status_code == 401
    assert "Invalid or missing API key" in response.json()["detail"]


def test_create_event_with_invalid_api_key(client, sample_event_payload):
    """Test that creating an event with invalid API key returns 401."""
    headers = {"X-API-Key": "invalid-key"}
    response = client.post("/v1/events", json=sample_event_payload, headers=headers)
    assert response.status_code == 401
    assert "Invalid or missing API key" in response.json()["detail"]


def test_list_events_without_api_key(client):
    """Test that listing events without API key returns 401."""
    response = client.get("/v1/events")
    assert response.status_code == 401


def test_get_event_without_api_key(client):
    """Test that getting a specific event without API key returns 401."""
    response = client.get("/v1/events/1?exnum=EX001")
    assert response.status_code == 401


def test_create_event_with_valid_api_key(client, api_headers, sample_event_payload):
    """Test that creating an event with valid API key succeeds."""
    response = client.post("/v1/events", json=sample_event_payload, headers=api_headers)
    assert response.status_code == 200
    assert "id" in response.json()
