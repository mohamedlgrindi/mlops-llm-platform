from fastapi import FastAPI
import pytest
from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)

def test_health_check():
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json()["status"] =="healthy"

def test_generate_invalid_input():

    payload = {
        "prompt": "Test prompt",
        "max_token": -50,
        "temperature": 0.7
    }
    response = client.post("/generate",json =payload)
    assert response.status_code == 422
