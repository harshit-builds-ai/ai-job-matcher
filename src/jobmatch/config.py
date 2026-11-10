"""Configuration read from environment variables (12-factor style)."""

from __future__ import annotations

import os
from dataclasses import dataclass

try:  # optional convenience: load a local .env file if python-dotenv is installed
    from dotenv import load_dotenv

    load_dotenv()
except ImportError:  # pragma: no cover
    pass


class ConfigError(RuntimeError):
    """Raised when required configuration (e.g. an API key) is missing."""


@dataclass(frozen=True)
class Settings:
    openai_api_key: str | None
    chat_model: str
    embedding_model: str

    @classmethod
    def from_env(cls) -> "Settings":
        return cls(
            openai_api_key=os.getenv("OPENAI_API_KEY") or None,
            chat_model=os.getenv("OPENAI_CHAT_MODEL", "gpt-4o-mini"),
            embedding_model=os.getenv("OPENAI_EMBEDDING_MODEL", "text-embedding-3-small"),
        )

    def require_api_key(self) -> str:
        if not self.openai_api_key:
            raise ConfigError("OPENAI_API_KEY is not set. Use offline mode or set the key.")
        return self.openai_api_key
