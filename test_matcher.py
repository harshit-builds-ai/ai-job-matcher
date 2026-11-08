import json

from jobmatch import matcher
from jobmatch.text import bow_similarity, cosine, find_skills

JD = "Graduate AI Engineer. Python, OpenAI API, prompt engineering, Docker, microservices, NLP, agile."
RESUME = "Built Python tools using the OpenAI API and prompt engineering. Experience with SQL and Docker."


class FakeLLM:
    def __init__(self, reply): self.reply, self.calls = reply, []
    def complete(self, system, user):
        self.calls.append((system, user)); return self.reply


class FakeEmbedder:
    def embed(self, texts): return [[1.0, 0.0], [1.0, 0.0]]


def test_find_skills_phrases():
    assert {"python", "openai api", "prompt engineering", "docker"} <= find_skills(RESUME + " python")


def test_missing_and_matched_skills():
    r = matcher.analyze(RESUME + " Python", JD)
    assert "microservices" in r["skills_missing"] and "nlp" in r["skills_missing"]
    assert "docker" in r["skills_matched"]
    assert r["similarity_method"] == "bag-of-words"


def test_embedding_path_used():
    r = matcher.analyze(RESUME, JD, embedder=FakeEmbedder())
    assert r["similarity"] == 1.0 and r["similarity_method"] == "embeddings"


def test_llm_json_with_code_fence_is_parsed_and_prompt_forbids_invention():
    reply = "```json\n" + json.dumps({"match_score": 70, "strengths": ["Python"], "gaps": [], "suggested_bullets": []}) + "\n```"
    llm = FakeLLM(reply)
    r = matcher.analyze(RESUME, JD, llm=llm)
    assert r["llm_analysis"]["match_score"] == 70
    assert "Never invent" in llm.calls[0][0]


def test_cosine_and_identical_text():
    assert cosine([1, 0], [0, 1]) == 0.0
    assert bow_similarity(JD, JD) > 0.99
