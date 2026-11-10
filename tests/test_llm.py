import pytest

from fakes import FakeEmbedder, FakeLLM
from jobmatch.llm import parse_json_response
from jobmatch.matcher import draft_cover_letter, llm_match
from jobmatch.prompts import ANALYSIS_SYSTEM


def test_parse_json_plain_fenced_and_with_extra_text():
    assert parse_json_response('{"a": 1}') == {"a": 1}
    assert parse_json_response('```json\n{"a": 1}\n```') == {"a": 1}
    assert parse_json_response('Here you go: {"a": 1} thanks') == {"a": 1}


@pytest.mark.parametrize("raw", ["no json here", "[1, 2]", "{broken"])
def test_parse_json_rejects_bad_replies(raw):
    with pytest.raises(ValueError):
        parse_json_response(raw)


def test_llm_match_uses_fakes_and_clamps_score():
    llm = FakeLLM()
    result = llm_match("python docker", "python kubernetes", llm, FakeEmbedder())
    assert result.mode == "llm"
    assert result.score == 82
    assert result.similarity == pytest.approx(0.8)
    assert result.gaps == ["Kubernetes"]
    assert llm.calls[0][2] is True  # JSON mode requested


def test_llm_match_handles_messy_model_output():
    llm = FakeLLM('{"match_score": 250, "strengths": "oops", "gaps": [" x ", ""]}')
    result = llm_match("python", "python", llm, FakeEmbedder())
    assert result.score == 100
    assert result.strengths == []
    assert result.gaps == ["x"]


def test_prompts_exclude_protected_attributes_and_invention():
    assert "protected attributes" in ANALYSIS_SYSTEM
    assert "Never invent" in ANALYSIS_SYSTEM


def test_cover_letter_is_drafted_by_llm():
    assert draft_cover_letter("python", "python", FakeLLM()).startswith("Dear")
