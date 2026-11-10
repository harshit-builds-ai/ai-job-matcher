"""One entry point shared by the CLI and the API."""

from __future__ import annotations

from .config import Settings
from .llm import EmbeddingClient, LLMClient, OpenAIClient
from .matcher import MatchResult, draft_cover_letter, llm_match, offline_match


def build_clients(settings: Settings | None = None) -> tuple[LLMClient, EmbeddingClient]:
    client = OpenAIClient(settings or Settings.from_env())
    return client, client


def run_match(
    resume: str,
    jd: str,
    use_llm: bool = False,
    cover_letter: bool = False,
    llm: LLMClient | None = None,
    embedder: EmbeddingClient | None = None,
) -> MatchResult:
    if cover_letter and not use_llm:
        raise ValueError("A cover letter needs LLM mode (use_llm=True)")

    if not use_llm:
        return offline_match(resume, jd)

    if llm is None or embedder is None:
        llm, embedder = build_clients()

    result = llm_match(resume, jd, llm, embedder)
    if cover_letter:
        result.cover_letter = draft_cover_letter(resume, jd, llm)
    return result
