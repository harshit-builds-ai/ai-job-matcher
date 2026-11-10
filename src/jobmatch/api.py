"""FastAPI microservice: POST /match, GET /health."""

from __future__ import annotations

from fastapi import Depends, FastAPI, HTTPException
from pydantic import BaseModel, Field

from .config import ConfigError
from .service import build_clients, run_match
from .text import MAX_CHARS

app = FastAPI(title="AI Job Matcher", version="0.1.0")


class MatchRequest(BaseModel):
    resume: str = Field(min_length=1, max_length=MAX_CHARS)
    jd: str = Field(min_length=1, max_length=MAX_CHARS)
    use_llm: bool = False
    cover_letter: bool = False


def get_client_factory():
    """Dependency returning the function that builds LLM clients (overridden in tests)."""
    return build_clients


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}


@app.post("/match")
def match(request: MatchRequest, client_factory=Depends(get_client_factory)) -> dict:
    if request.cover_letter and not request.use_llm:
        raise HTTPException(status_code=400, detail="cover_letter requires use_llm=true")
    try:
        llm = embedder = None
        if request.use_llm:
            llm, embedder = client_factory()
        result = run_match(
            request.resume,
            request.jd,
            use_llm=request.use_llm,
            cover_letter=request.cover_letter,
            llm=llm,
            embedder=embedder,
        )
    except ConfigError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=502, detail=f"LLM reply could not be used: {exc}") from exc
    return result.to_dict()
