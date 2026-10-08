import numpy as np
import pytest

from src.references import RuleIdentity, tfidf_fit_score, tfidf_pipeline, training_set


def test_rule_identity_majority_tie_and_absent_rule():
    rules = ["r1", "r1", "r1", "r2", "r2", "r3"]
    y = [True, True, False, True, False, False]
    ri = RuleIdentity().fit(rules, y)
    assert ri.predict(["r1", "r2", "r3", "unseen"]) == ["Attack", "Attack", "Non-Attack", "Non-Attack"]
    s = ri.score(["r1", "r2", "r3", "unseen"])
    assert s[0] == pytest.approx(2 / 3) and s[1] == 0.5 and s[2] == 0.0
    assert s[3] == pytest.approx(3 / 6)                       # absent rule: overall training Attack rate


def test_absent_rule_is_non_attack_even_when_training_is_mostly_attack():
    ri = RuleIdentity().fit(["r1", "r1", "r2"], [True, True, True])
    assert ri.predict(["unseen"]) == ["Non-Attack"]           # fixed in the implementation (§4)


def test_hard_rule_equals_score_threshold_for_seen_rules():
    g = np.random.Generator(np.random.PCG64(1))
    rules = [f"r{i}" for i in g.integers(0, 15, 300)]
    y = list(g.integers(0, 2, 300).astype(bool))
    ri = RuleIdentity().fit(rules, y)
    seen = sorted(set(rules))
    assert ri.predict(seen) == ["Attack" if s >= 0.5 else "Non-Attack" for s in ri.score(seen)]


def test_training_set_drops_every_test_content_key():
    frame = [{"key": k, "rule_name": "r"} for k in ("k1", "k2", "k3", "k4")]
    assert [f["key"] for f in training_set(frame, {"k2", "k4", "k9"})] == ["k1", "k3"]


def test_tfidf_pipeline_is_the_protocol_configuration():
    hv, tf, lr = (s for _, s in tfidf_pipeline().steps)
    assert (hv.analyzer, hv.ngram_range, hv.n_features, hv.alternate_sign, hv.norm, hv.lowercase) == \
        ("char", (3, 5), 2 ** 20, False, None, False)
    assert tf.sublinear_tf is True
    assert (lr.C, lr.penalty, lr.solver, lr.class_weight, lr.max_iter, lr.random_state) == \
        (1.0, "l2", "liblinear", "balanced", 1000, 0)


def test_tfidf_scores_are_probabilities_of_attack():
    train = ["union select password from users"] * 6 + ["get /index.html http/1.1"] * 6
    y = [True] * 6 + [False] * 6
    p = tfidf_fit_score(train, y, ["union select 1", "get /about.html http/1.1"])
    assert 0 <= p.min() and p.max() <= 1 and p[0] > 0.5 > p[1]


def test_d10_published_record_is_the_test_input_and_unmatched_rows_are_kept(monkeypatch):
    from src import references
    from src.common import content_key

    from .conftest import fake_record

    data = [fake_record(i, "Attack" if i % 2 else "Non-Attack", f"r{i % 3}") for i in range(8)]
    frame = [{"row_index": i, "key": content_key(r), "label": r["Label"], "rule_name": r["rule_name"]}
             for i, r in enumerate(data)]
    shown = {k: v for k, v in data[0].items() if k != "Label"}
    shown["sip"] = "203.0.113.9"                                # published record: other random IP, same key
    unmatched = {**{k: v for k, v in data[1].items() if k != "Label"}, "uri": "uri-not-in-dataset"}
    rows = [{"row": 0, "uid": "p0", "key": content_key(shown), "rule_name": "r0", "record": shown},
            {"row": 1, "uid": "p1", "key": content_key(unmatched), "rule_name": "r1", "record": unmatched}]
    seen = {}

    def fake_fit(train_texts, y, test_texts):
        seen["train"], seen["test"] = train_texts, test_texts
        return np.full(len(test_texts), 0.7)

    monkeypatch.setattr(references, "tfidf_fit_score", fake_fit)
    out, summary = references.predict_test_set(frame, data, rows, ("a",))
    assert "203.0.113.9" in seen["test"][0]                     # test text from the published record
    assert all("203.0.113.9" not in t for t in seen["train"])   # training text from dataset rows
    assert len(seen["train"]) == 7                              # exact content-key duplicate of row 0 excluded
    assert [o["matched_to_dataset"] for o in out] == [True, False]
    assert summary["unmatched_to_dataset"] == 1 and summary["test_rows"] == 2
