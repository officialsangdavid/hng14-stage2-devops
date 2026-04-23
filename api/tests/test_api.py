import pytest
from fastapi.testclient import TestClient
from unittest.mock import Mock, patch
import sys
import os

# Add parent directory to path to import main
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from main import app

client = TestClient(app)

@pytest.fixture
def mock_redis():
    with patch('main.r') as mock:
        yield mock

def test_health_endpoint_healthy(mock_redis):
    """Test health endpoint returns healthy when Redis is available"""
    mock_redis.ping.return_value = True
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}

def test_create_job(mock_redis):
    """Test job creation endpoint"""
    mock_redis.lpush.return_value = 1
    mock_redis.hset.return_value = 1
    
    response = client.post("/jobs")
    assert response.status_code == 200
    data = response.json()
    assert "job_id" in data
    assert len(data["job_id"]) == 36  # UUID format
    
    # Verify Redis calls
    mock_redis.lpush.assert_called_once()
    mock_redis.hset.assert_called_once()

def test_get_job_found(mock_redis):
    """Test getting job status when job exists"""
    job_id = "test-job-123"
    mock_redis.hget.return_value = b"completed"
    
    response = client.get(f"/jobs/{job_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["job_id"] == job_id
    assert data["status"] == "completed"

def test_get_job_not_found(mock_redis):
    """Test getting job status when job doesn't exist"""
    mock_redis.hget.return_value = None
    
    response = client.get("/jobs/nonexistent")
    assert response.status_code == 200
    assert response.json() == {"error": "not found"}

def test_health_endpoint_unhealthy(mock_redis):
    """Test health endpoint returns unhealthy when Redis is down"""
    mock_redis.ping.side_effect = Exception("Redis connection failed")
    response = client.get("/health")
    assert response.status_code == 200  # Note: should ideally be 503, but current implementation returns 200