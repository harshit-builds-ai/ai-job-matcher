"""Fake LLM clients so tests never touch the network."""

import json


class FakeLLM:
    def __init__(self, reply: str | None = None):
        self.calls = []
        self.reply = reply or json.dumps(
            {
                "match_score": 82,
                "strengths": ["Python", "RAG project"],
                "gaps": ["Kubernetes"],
                "suggested_bullets": ["Built a RAG chatbot in Python with embeddings."],
            }
        )

    def complete(self, system, user, json_mode=False):
        self.calls.append((system, user, json_mode))
        return self.reply if json_mode else "Dear Hiring Manager, ..."


class FakeEmbedder:
    def embed(self, texts):
        return [[1.0, 0.0] if i == 0 else [0.8, 0.6] for i, _ in enumerate(texts)]
