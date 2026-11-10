from pathlib import Path

from jobmatch.matcher import offline_match
from jobmatch.skills import extract_skills

EXAMPLES = Path(__file__).resolve().parent.parent / "examples"


def test_extract_skills_handles_aliases_and_boundaries():
    skills = extract_skills("Experienced with Google Cloud, k8s and JavaScript. No javaland.")
    assert {"gcp", "kubernetes", "javascript"} <= skills
    assert "java" not in skills  # "javascript"/"javaland" must not match "java"


def test_offline_match_on_examples():
    resume = (EXAMPLES / "sample_resume.txt").read_text(encoding="utf-8")
    jd = (EXAMPLES / "sample_jd.txt").read_text(encoding="utf-8")
    result = offline_match(resume, jd)
    assert result.mode == "offline"
    assert 0 <= result.score <= 100
    assert "python" in result.matched_skills
    assert "kubernetes" in result.missing_skills


def test_offline_match_with_no_jd_skills_scores_from_similarity_only():
    result = offline_match("python developer", "we sell shoes")
    assert result.matched_skills == [] and result.missing_skills == []
    assert 0 <= result.score <= 100
