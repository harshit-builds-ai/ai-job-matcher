from fastapi.testclient import TestClient

from fakes import FakeEmbedder, FakeLLM
from jobmatch.api import app, get_client_factory

client = TestClient(app)


def test_health():
    assert client.get("/health").json() == {"status": "ok"}


def test_match_offline():
    response = client.post("/match", json={"resume": "python docker", "jd": "python kubernetes"})
    assert response.status_code == 200
    body = response.json()
    assert body["mode"] == "offline"
    assert body["matched_skills"] == ["python"]


def test_match_llm_with_fake_clients_and_cover_letter():
    app.dependency_overrides[get_client_factory] = lambda: (lambda: (FakeLLM(), FakeEmbedder()))
    try:
        response = client.post(
            "/match",
            json={"resume": "python", "jd": "python", "use_llm": True, "cover_letter": True},
        )
    finally:
        app.dependency_overrides.clear()
    assert response.status_code == 200
    body = response.json()
    assert body["mode"] == "llm" and body["score"] == 82
    assert body["cover_letter"].startswith("Dear")


def test_llm_mode_without_api_key_returns_503(monkeypatch):
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    response = client.post("/match", json={"resume": "a", "jd": "b", "use_llm": True})
    assert response.status_code == 503


def test_cover_letter_requires_llm_and_empty_input_rejected():
    assert client.post("/match", json={"resume": "a", "jd": "b", "cover_letter": True}).status_code == 400
    assert client.post("/match", json={"resume": "", "jd": "b"}).status_code == 422
