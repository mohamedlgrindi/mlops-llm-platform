from fastapi import FastAPI
import pytest
from fastapi.testclient import TestClient

from app.main import app


@pytest.fixture
def client():
    with TestClient(app) as test_client:
        yield test_client


def test_health_check(client):
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json()["status"] =="healthy"

def test_generate_invalid_input(client):

    payload = {
        "prompt": "Test prompt",
        "max_tokens": -50,
        "temperature": 0.7
    }
    response = client.post("/generate",json =payload)
    assert response.status_code == 422

def test_generate_endpoint_valid(client):

    payload = {
            "prompt": "Test prompt",
            "max_tokens": 50,
            "temperature": 0.7
        }
    response = client.post("/generate",json=payload)

    assert response.status_code == 200
    assert response.headers["content-type"].startswith("text/event-stream")