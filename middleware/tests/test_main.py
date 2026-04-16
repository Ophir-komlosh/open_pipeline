from fastapi.testclient import TestClient
from consts import *
from main import app

client = TestClient(app)


def test_health_check():
    response = client.get("/health")

    assert response.status_code == OK_STATUS_CODE
    assert response.json() == {"status": "ok"}