"""Rule-based skill extraction used by the offline baseline."""

from __future__ import annotations

import re

# canonical skill -> accepted spellings (all lowercase)
SKILLS: dict[str, list[str]] = {
    "python": ["python"],
    "java": ["java"],
    "javascript": ["javascript", "js"],
    "typescript": ["typescript"],
    "sql": ["sql"],
    "fastapi": ["fastapi"],
    "flask": ["flask"],
    "django": ["django"],
    "docker": ["docker", "containers", "container-based"],
    "kubernetes": ["kubernetes", "k8s"],
    "aws": ["aws", "amazon web services"],
    "azure": ["azure"],
    "gcp": ["gcp", "google cloud", "google cloud platform"],
    "cloud-native": ["cloud-native", "cloud native"],
    "microservices": ["microservices", "microservice"],
    "12-factor": ["12-factor", "twelve-factor", "12 factor"],
    "ci/cd": ["ci/cd", "cicd", "github actions", "jenkins"],
    "devops": ["devops"],
    "git": ["git", "github"],
    "rest api": ["rest api", "rest apis", "restful"],
    "linux": ["linux"],
    "machine learning": ["machine learning", "ml"],
    "deep learning": ["deep learning"],
    "nlp": ["nlp", "natural language processing"],
    "llm": ["llm", "llms", "language models", "language model"],
    "genai": ["genai", "generative ai", "gen ai"],
    "rag": ["rag", "retrieval-augmented generation", "retrieval augmented generation"],
    "prompt engineering": ["prompt engineering", "prompt design", "prompts"],
    "embeddings": ["embeddings", "embedding"],
    "tokenization": ["tokenization", "tokenisation"],
    "transformers": ["transformers", "transformer"],
    "openai": ["openai"],
    "gemini": ["gemini"],
    "langchain": ["langchain"],
    "llamaindex": ["llamaindex", "llama-index"],
    "hugging face": ["hugging face", "huggingface"],
    "pytorch": ["pytorch"],
    "tensorflow": ["tensorflow"],
    "pandas": ["pandas"],
    "numpy": ["numpy"],
    "scikit-learn": ["scikit-learn", "sklearn"],
    "pytest": ["pytest"],
    "agile": ["agile"],
    "scrum": ["scrum"],
    "ai ethics": ["ai ethics", "bias mitigation", "responsible ai"],
    "data engineering": ["data engineering", "data pipelines", "data pipeline"],
    "power bi": ["power bi", "powerbi"],
    "react": ["react"],
    "node.js": ["node.js", "nodejs"],
    "postgresql": ["postgresql", "postgres"],
    "mongodb": ["mongodb"],
}

_PATTERNS = {
    skill: re.compile(
        r"(?<![a-z0-9+#])(?:" + "|".join(re.escape(a) for a in aliases) + r")(?![a-z0-9+#])"
    )
    for skill, aliases in SKILLS.items()
}


def extract_skills(text: str) -> set[str]:
    """Return the canonical skills mentioned in ``text``."""
    lowered = text.lower()
    return {skill for skill, pattern in _PATTERNS.items() if pattern.search(lowered)}
