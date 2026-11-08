"""Thin wrappers around the OpenAI API. The matcher only depends on the small
`complete()` / `embed()` interfaces, so tests can use fakes and no network is needed."""
from typing import Protocol

from . import config


class LLM(Protocol):
    def complete(self, system: str, user: str) -> str: ...


class Embedder(Protocol):
    def embed(self, texts: list[str]) -> list[list[float]]: ...


def _client():
    if not config.OPENAI_API_KEY:
        raise RuntimeError("OPENAI_API_KEY is not set. See .env.example")
    from openai import OpenAI  # imported lazily so offline mode needs no SDK
    return OpenAI(api_key=config.OPENAI_API_KEY)


class OpenAILLM:
    def __init__(self, model: str | None = None):
        self.client, self.model = _client(), model or config.OPENAI_MODEL

    def complete(self, system: str, user: str) -> str:
        resp = self.client.chat.completions.create(
            model=self.model,
            temperature=0.2,
            messages=[{"role": "system", "content": system}, {"role": "user", "content": user}],
        )
        return resp.choices[0].message.content or ""


class OpenAIEmbedder:
    def __init__(self, model: str | None = None):
        self.client, self.model = _client(), model or config.OPENAI_EMBEDDING_MODEL

    def embed(self, texts: list[str]) -> list[list[float]]:
        resp = self.client.embeddings.create(model=self.model, input=texts)
        return [d.embedding for d in resp.data]
