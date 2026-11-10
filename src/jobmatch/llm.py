"""LLM and embedding clients behind small interfaces, so tests can use fakes."""

from __future__ import annotations

import json
import re
from typing import Protocol

from .config import Settings


class LLMClient(Protocol):
    def complete(self, system: str, user: str, json_mode: bool = False) -> str: ...


class EmbeddingClient(Protocol):
    def embed(self, texts: list[str]) -> list[list[float]]: ...


class OpenAIClient:
    """Chat + embeddings through the official OpenAI SDK (imported lazily)."""

    def __init__(self, settings: Settings):
        from openai import OpenAI  # lazy: offline mode does not need the SDK

        self._client = OpenAI(api_key=settings.require_api_key(), timeout=30.0, max_retries=2)
        self._chat_model = settings.chat_model
        self._embedding_model = settings.embedding_model

    def complete(self, system: str, user: str, json_mode: bool = False) -> str:
        kwargs = {"response_format": {"type": "json_object"}} if json_mode else {}
        response = self._client.chat.completions.create(
            model=self._chat_model,
            messages=[{"role": "system", "content": system}, {"role": "user", "content": user}],
            temperature=0.2,
            **kwargs,
        )
        return response.choices[0].message.content or ""

    def embed(self, texts: list[str]) -> list[list[float]]:
        response = self._client.embeddings.create(model=self._embedding_model, input=texts)
        return [item.embedding for item in response.data]


_FENCE = re.compile(r"^```(?:json)?\s*|\s*```$", re.IGNORECASE)


def parse_json_response(raw: str) -> dict:
    """Parse model output as JSON, tolerating code fences or extra text around it."""
    cleaned = _FENCE.sub("", raw.strip())
    try:
        data = json.loads(cleaned)
    except json.JSONDecodeError:
        start, end = cleaned.find("{"), cleaned.rfind("}")
        if start == -1 or end <= start:
            raise ValueError("Model reply did not contain a JSON object") from None
        try:
            data = json.loads(cleaned[start : end + 1])
        except json.JSONDecodeError as exc:
            raise ValueError(f"Model reply was not valid JSON: {exc}") from exc
    if not isinstance(data, dict):
        raise ValueError("Model reply JSON must be an object")
    return data
