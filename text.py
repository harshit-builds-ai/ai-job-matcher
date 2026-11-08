"""NLP basics: tokenization, skill extraction and bag-of-words similarity."""
import math
import re
from collections import Counter

STOPWORDS = {
    "the", "and", "for", "with", "you", "your", "are", "will", "our", "from", "that", "this",
    "have", "has", "can", "use", "using", "such", "including", "all", "any", "into", "their",
    "who", "not", "but", "its", "work", "role", "team", "support", "ability", "strong", "good",
}

# Curated phrases to look for. Matching is on whole words/phrases, case-insensitive.
SKILLS = [
    "python", "java", "sql", "genai", "generative ai", "llm", "openai api", "openai",
    "prompt engineering", "nlp", "tokenization", "embeddings", "transformers",
    "machine learning", "data engineering", "data pipeline", "etl", "pandas",
    "docker", "kubernetes", "microservices", "containers", "cloud-native", "12-factor",
    "devops", "ci/cd", "git", "github", "rest api", "fastapi", "aws", "azure", "gcp",
    "agile", "scrum", "power bi", "excel", "bias mitigation", "ai ethics",
]


def tokenize(text: str) -> list[str]:
    tokens = re.findall(r"[a-z0-9][a-z0-9+#./-]*", text.lower())
    return [t.strip("./-") for t in tokens if len(t.strip("./-")) > 2 and t not in STOPWORDS]


def find_skills(text: str) -> set[str]:
    low = text.lower()
    found = set()
    for skill in SKILLS:
        if re.search(r"(?<![a-z0-9])" + re.escape(skill) + r"(?![a-z0-9])", low):
            found.add(skill)
    return found


def cosine(a: list[float], b: list[float]) -> float:
    dot = sum(x * y for x, y in zip(a, b))
    na, nb = math.sqrt(sum(x * x for x in a)), math.sqrt(sum(y * y for y in b))
    return dot / (na * nb) if na and nb else 0.0


def bow_similarity(text_a: str, text_b: str) -> float:
    """Offline baseline: cosine similarity between word-count vectors."""
    ca, cb = Counter(tokenize(text_a)), Counter(tokenize(text_b))
    vocab = sorted(set(ca) | set(cb))
    return cosine([ca[w] for w in vocab], [cb[w] for w in vocab])
