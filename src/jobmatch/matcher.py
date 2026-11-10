"""Matching logic: an offline baseline and an LLM-assisted analysis."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field

from . import prompts
from .llm import EmbeddingClient, LLMClient, parse_json_response
from .skills import extract_skills
from .text import bow_cosine, clip, cosine


@dataclass
class MatchResult:
    mode: str  # "offline" or "llm"
    score: int  # 0-100
    similarity: float  # 0-1
    matched_skills: list[str]
    missing_skills: list[str]
    strengths: list[str] = field(default_factory=list)
    gaps: list[str] = field(default_factory=list)
    suggested_bullets: list[str] = field(default_factory=list)
    cover_letter: str | None = None

    def to_dict(self) -> dict:
        return asdict(self)


def _clamp_score(value) -> int:
    try:
        return max(0, min(100, int(round(float(value)))))
    except (TypeError, ValueError):
        return 0


def _str_list(value) -> list[str]:
    if not isinstance(value, list):
        return []
    return [str(item).strip() for item in value if str(item).strip()]


def offline_match(resume: str, jd: str) -> MatchResult:
    """Skill overlap + bag-of-words similarity. Needs no API key or network."""
    resume, jd = clip(resume), clip(jd)
    resume_skills, jd_skills = extract_skills(resume), extract_skills(jd)
    matched = sorted(jd_skills & resume_skills)
    missing = sorted(jd_skills - resume_skills)
    coverage = len(matched) / len(jd_skills) if jd_skills else 0.0
    similarity = bow_cosine(resume, jd)
    score = round(100 * (0.7 * coverage + 0.3 * similarity))
    return MatchResult(
        mode="offline",
        score=_clamp_score(score),
        similarity=round(similarity, 4),
        matched_skills=matched,
        missing_skills=missing,
    )


def llm_match(resume: str, jd: str, llm: LLMClient, embedder: EmbeddingClient) -> MatchResult:
    """Offline baseline enriched with embedding similarity and a structured LLM analysis."""
    resume, jd = clip(resume), clip(jd)
    baseline = offline_match(resume, jd)

    vec_resume, vec_jd = embedder.embed([resume, jd])
    similarity = cosine(vec_resume, vec_jd)

    raw = llm.complete(
        prompts.ANALYSIS_SYSTEM,
        prompts.ANALYSIS_USER.format(resume=resume, jd=jd),
        json_mode=True,
    )
    analysis = parse_json_response(raw)

    return MatchResult(
        mode="llm",
        score=_clamp_score(analysis.get("match_score")),
        similarity=round(similarity, 4),
        matched_skills=baseline.matched_skills,
        missing_skills=baseline.missing_skills,
        strengths=_str_list(analysis.get("strengths")),
        gaps=_str_list(analysis.get("gaps")),
        suggested_bullets=_str_list(analysis.get("suggested_bullets")),
    )


def draft_cover_letter(resume: str, jd: str, llm: LLMClient) -> str:
    """Draft a short cover letter using only facts from the resume."""
    return llm.complete(
        prompts.COVER_LETTER_SYSTEM,
        prompts.COVER_LETTER_USER.format(resume=clip(resume), jd=clip(jd)),
    ).strip()
