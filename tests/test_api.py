from fastapi.testclient import TestClient

from jobmatch import config
from jobmatch.api import app

client = TestClient(app)

RESUME = "Python developer. Built REST APIs with FastAPI and Docker. Agile team."
JD = "We need a Python developer with Docker, prompt engineering and Agile experience."


def test_health():
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json() == {"status": "ok"}


def test_match_offline_baseline():
    r = client.post("/match", json={"resume": RESUME, "jd": JD, "use_llm": False})
    assert r.status_code == 200
    body = r.json()
    assert "python" in body["skills_matched"]
    assert 0.0 <= body["similarity"] <= 1.0


def test_match_llm_without_key_is_rejected(monkeypatch):
    monkeypatch.setattr(config, "OPENAI_API_KEY", "")
    r = client.post("/match", json={"resume": RESUME, "jd": JD, "use_llm": True})
    assert r.status_code == 400


def test_match_requires_both_fields():
    r = client.post("/match", json={"resume": RESUME})
    assert r.status_code == 422
