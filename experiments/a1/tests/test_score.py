import math

from src.score import extract_score

LT1 = {"A": [10], "N": [20, 5, 10], "k": 1}
LT2 = {"A": [7, 10], "N": [7, 20], "k": 2}


def pos(tok_id, top):
    return {"id": tok_id, "top_logprobs": [{"id": i, "logprob": math.log(p)} for i, p in top]}


def test_both_labels_in_top20_gives_renormalised_score():
    s = extract_score([pos(10, [(10, 0.6), (20, 0.2), (3, 0.1)])], LT1)
    assert s["available"] and abs(s["s"] - 0.75) < 1e-12


def test_one_label_missing_is_unavailable_without_substitution():
    s = extract_score([pos(10, [(10, 0.99), (3, 0.01)])], LT1)
    assert not s["available"] and "s" not in s and s["reason"] == "Non-Attack absent from top-20"


def test_generated_prefix_must_match_when_k_above_1():
    ok = extract_score([pos(7, [(7, 1.0)]), pos(10, [(10, 0.5), (20, 0.5)])], LT2)
    assert ok["available"] and abs(ok["s"] - 0.5) < 1e-12
    bad = extract_score([pos(8, [(8, 1.0)]), pos(10, [(10, 0.5), (20, 0.5)])], LT2)
    assert not bad["available"]
