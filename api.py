"""REST microservice: uvicorn jobmatch.api:app --app-dir src"""
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from . import config, matcher

app = FastAPI(title="AI Job Matcher", version="1.0")


class MatchRequest(BaseModel):
    resume: str
    jd: str
    use_llm: bool = False


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}


@app.post("/match")
def match(req: MatchRequest) -> dict:
    llm = embedder = None
    if req.use_llm:
        if not config.OPENAI_API_KEY:
            raise HTTPException(status_code=400, detail="OPENAI_API_KEY not configured")
        from .llm import OpenAIEmbedder, OpenAILLM
        llm, embedder = OpenAILLM(), OpenAIEmbedder()
    return matcher.analyze(req.resume, req.jd, llm, embedder)
