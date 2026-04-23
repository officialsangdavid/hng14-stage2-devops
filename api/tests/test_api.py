import os
from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient

os.environ["REDIS_HOST"] = "localhost"
os.environ["REDIS_PORT"] = "6379"

from main import app  # noqa: E402

client = TestClient(app)


@pytest.fixture
def mock_redis():
    with patch("main.r") as mock_r:
        yield mock_r


def test_health_endpoint(mock_redis):
    mock_redis.ping.return_value = True
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}


def test_submit_job(mock_redis):
    mock_redis.hset.return_value = True
    mock_redis.lpush.return_value = True
    response = client.post("/submit")
    assert response.status_code == 200
    data = response.json()
    assert "job_id" in data


def test_get_status_completed(mock_redis):
    mock_redis.hget.return_value = b"completed"
    response = client.get("/status/test-job-id")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "completed"


def test_get_status_not_found(mock_redis):
    mock_redis.hget.return_value = None
    response = client.get("/status/nonexistent-job")
    assert response.status_code == 404


def test_get_status_queued(mock_redis):
    mock_redis.hget.return_value = b"queued"
    response = client.get("/status/test-job-id")
    assert response.status_code == 200
    assert response.json()["status"] == "queued"
