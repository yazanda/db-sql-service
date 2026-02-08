"""Tests for health check endpoint."""
import pytest


def test_health_check(client):
    """Test the health check endpoint."""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_health_check_no_auth_required(client):
    """Test that health check doesn't require authentication."""
    response = client.get("/health")
    assert response.status_code == 200
    assert "status" in response.json()
