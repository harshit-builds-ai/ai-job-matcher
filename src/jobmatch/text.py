"""Small text helpers: tokenizing and cosine similarity."""

from __future__ import annotations

import math
import re
from collections import Counter

MAX_CHARS = 20_000  # hard cap on input size sent anywhere

_WORD = re.compile(r"[a-z0-9+#.]+")

STOPWORDS = frozenset(
    """a an and are as at be by for from has have in is it its of on or that the this to
    was were will with you your we our they their i he she not but if so than then them
    can able about into over under more most such per via etc""".split()
)


def clip(text: str, limit: int = MAX_CHARS) -> str:
    """Trim very long inputs so a single request cannot become huge."""
    return text[:limit]


def tokenize(text: str) -> list[str]:
    tokens = []
    for raw in _WORD.findall(text.lower()):
        token = raw.strip(".")
        if token and token not in STOPWORDS:
            tokens.append(token)
    return tokens


def bow_cosine(a: str, b: str) -> float:
    """Cosine similarity of two texts using simple bag-of-words counts."""
    ca, cb = Counter(tokenize(a)), Counter(tokenize(b))
    if not ca or not cb:
        return 0.0
    dot = sum(ca[t] * cb[t] for t in ca.keys() & cb.keys())
    norm = math.sqrt(sum(v * v for v in ca.values())) * math.sqrt(sum(v * v for v in cb.values()))
    return dot / norm if norm else 0.0


def cosine(v1: list[float], v2: list[float]) -> float:
    """Cosine similarity of two embedding vectors."""
    if len(v1) != len(v2):
        raise ValueError("Vectors must have the same length")
    dot = sum(x * y for x, y in zip(v1, v2))
    n1 = math.sqrt(sum(x * x for x in v1))
    n2 = math.sqrt(sum(y * y for y in v2))
    return dot / (n1 * n2) if n1 and n2 else 0.0
