import pytest

from jobmatch.text import bow_cosine, cosine, tokenize


def test_tokenize_drops_stopwords_and_keeps_tech_tokens():
    tokens = tokenize("The C++ and Node.js developer, with Python.")
    assert "c++" in tokens and "node.js" in tokens and "python" in tokens
    assert "the" not in tokens


def test_bow_cosine_identical_and_disjoint():
    assert bow_cosine("python sql docker", "python sql docker") == pytest.approx(1.0)
    assert bow_cosine("python", "cooking recipes") == 0.0
    assert bow_cosine("", "python") == 0.0


def test_cosine_vectors():
    assert cosine([1, 0], [1, 0]) == pytest.approx(1.0)
    assert cosine([1, 0], [0, 1]) == pytest.approx(0.0)
    assert cosine([0, 0], [1, 1]) == 0.0
    with pytest.raises(ValueError):
        cosine([1], [1, 2])
