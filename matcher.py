"""Core logic: baseline (offline) analysis, optional embeddings, optional LLM analysis."""
import json
import re

from . import prompts
from .llm import LLM, Embedder
from .text import bow_similarity, cosine, find_skills


def parse_json(raw: str) -> dict:
    """LLMs sometimes wrap JSON in markdown fences or add text; recover the object."""
    cleaned = re.sub(r"^```(?:json)?|```$", "", raw.strip(), flags=re.MULTILINE).strip()
    try:
        return json.loads(cleaned)
    except json.JSONDecodeError:
        m = re.search(r"\{.*\}", cleaned, flags=re.DOTALL)
        if not m:
            raise ValueError("Model did not return JSON")
        return json.loads(m.group(0))


def analyze(resume: str, jd: str, llm: LLM | None = None, embedder: Embedder | None = None) -> dict:
    jd_skills, resume_skills = find_skills(jd), find_skills(resume)
    if embedder is not None:
        va, vb = embedder.embed([resume, jd])
        similarity, method = cosine(va, vb), "embeddings"
    else:
        similarity, method = bow_similarity(resume, jd), "bag-of-words"

    result = {
        "similarity": round(similarity, 3),
        "similarity_method": method,
        "skills_matched": sorted(jd_skills & resume_skills),
        "skills_missing": sorted(jd_skills - resume_skills),
        "skill_coverage": round(len(jd_skills & resume_skills) / len(jd_skills), 2) if jd_skills else None,
    }
    if llm is not None:
        raw = llm.complete(prompts.ANALYSIS_SYSTEM, prompts.ANALYSIS_USER.format(jd=jd, resume=resume))
        result["llm_analysis"] = parse_json(raw)
    return result


def cover_letter(resume: str, jd: str, llm: LLM) -> str:
    return llm.complete(prompts.COVER_LETTER_SYSTEM, prompts.COVER_LETTER_USER.format(jd=jd, resume=resume)).strip()
