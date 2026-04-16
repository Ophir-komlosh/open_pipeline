from fastapi.testclient import TestClient
from main import app
import main as main
from tests.fixtures import *
from consts import *

client = TestClient(app)


def test_health_check():
    response = client.get("/health")

    assert response.status_code == OK_STATUS_CODE
    assert response.json() == {"status": "ok"}

def test_ready_check(monkeypatch):
    monkeypatch.setattr(main, "OPENAI_API_KEY", "test-key")

    response = client.get("/ready")

    assert response.status_code == OK_STATUS_CODE

    data = response.json()
    assert data["status"] == "ready"
    assert data["has_api_key"] is True

def test_models_returns_openai_compatible_shape():
    response = client.get(FULL_MODELS_PATH)

    assert response.status_code == OK_STATUS_CODE

    data = response.json()
    assert data["object"] == "list"
    assert isinstance(data["data"], list)
    assert data["data"][FIRST_MODEL_INDEX]["id"] == CHAT_MODEL
    assert data["data"][FIRST_MODEL_INDEX]["object"] == "model"

def test_missing_api_key(monkeypatch):
    monkeypatch.setattr(main, "OPENAI_API_KEY", None)

    response = client.post(
        FULL_COMPLETIONS_PATH,
        json={
            "model": CHAT_MODEL,
            "messages": [{MESSAGE_ROLE: USER_ROLE, MESSAGE_CONTENT: CONTENT}],
        },
    )

    assert response.status_code == INTERNAL_SERVER_ERROR_CODE
    body = response.json()
    assert body["error"] == CONFIGURATION_ERROR


def test_message_missing(monkeypatch):
    monkeypatch.setattr(main, "OPENAI_API_KEY", "test-key")

    response = client.post(
        FULL_COMPLETIONS_PATH,
        json={
            "model": CHAT_MODEL,
        },
    )

    assert response.status_code == BAD_REQUEST_CODE
    body = response.json()
    assert body["error"] == INVALID_REQUEST


def test_message_empty(monkeypatch):
    monkeypatch.setattr(main, "OPENAI_API_KEY", "test-key")

    response = client.post(
        FULL_COMPLETIONS_PATH,
        json={
            "model": CHAT_MODEL,
            "messages": [],
        },
    )

    assert response.status_code == BAD_REQUEST_CODE
    body = response.json()
    assert body["error"] == INVALID_REQUEST