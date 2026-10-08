from collections import Counter

import numpy as np
import pytest
from sklearn.metrics import roc_auc_score

from src.metrics import (auroc, auroc_with_bounds, bootstrap_indices, cluster_bootstrap_indices, counts, encode,
                         from_counts, hard_metrics, paired_bootstrap, percentile_ci, valid_coverage)

A, N = "Attack", "Non-Attack"


def test_hand_computed_confusion_and_rates():
    m = hard_metrics([A, A, A, A, N, N, N, N, N], [A, A, A, N, A, N, N, N, N])
    assert (m["TP"], m["FP"], m["TN"], m["FN"]) == (3, 1, 4, 1)
    assert m["tpr"] == pytest.approx(0.75)
    assert m["fpr"] == pytest.approx(0.2)
    assert m["precision"] == pytest.approx(0.75)
    assert m["f1"] == pytest.approx(2 * 3 / (2 * 3 + 1 + 1))
    assert m["balanced_accuracy"] == pytest.approx((0.75 + 0.8) / 2)


def test_invalid_counts_as_failure_by_default_and_is_dropped_in_sensitivity():
    y, p = [A, A, N, N], [A, None, N, None]
    prim = hard_metrics(y, p)
    assert (prim["TP"], prim["FN"], prim["TN"], prim["FP"]) == (1, 1, 1, 1)
    sens = hard_metrics(y, p, invalid="exclude")
    assert (sens["TP"], sens["FN"], sens["TN"], sens["FP"], sens["n"]) == (1, 0, 1, 0, 2)
    assert prim["n_invalid"] == 2
    assert valid_coverage(p) == 0.5


def test_always_attack_on_balanced_sample_matches_the_protocol_example():
    m = hard_metrics([A] * 50 + [N] * 50, [A] * 100)
    assert m["precision"] == 0.5 and m["tpr"] == 1.0 and m["fpr"] == 1.0
    assert m["f1"] == pytest.approx(2 / 3)


def test_undefined_values():
    m = from_counts({"TP": 0, "FP": 0, "TN": 5, "FN": 5})
    assert m["precision"] is None and m["f1"] == 0.0
    assert from_counts({"TP": 0, "FP": 0, "TN": 5, "FN": 0})["tpr"] is None


def test_weights_enter_counts():
    t, p = encode([A, A, N], [A, N, A])
    c = counts(t, p, w=[2.0, 0.5, 1.5])
    assert (c["TP"], c["FN"], c["FP"], c["TN"]) == (2.0, 0.5, 1.5, 0.0)


def test_encode_rejects_unknown_labels():
    with pytest.raises(ValueError):
        encode([A], ["attack"])


@pytest.mark.parametrize("seed", range(20))
def test_auroc_equals_sklearn_with_ties_and_weights(seed):
    g = np.random.Generator(np.random.PCG64(seed))
    y = g.integers(0, 2, 200).astype(bool)
    s = g.integers(0, 7, 200) / 6.0
    w = g.uniform(0.5, 1.5, 200)
    assert auroc(y, s) == pytest.approx(roc_auc_score(y, s), abs=1e-12)
    assert auroc(y, s, w) == pytest.approx(roc_auc_score(y, s, sample_weight=w), abs=1e-12)


def test_auroc_single_class_is_undefined():
    assert auroc([True, True], [0.1, 0.9]) is None


def test_auroc_bounds_bracket_and_reduce_to_primary_when_all_available():
    y = [True, True, False, False, True, False]
    full = auroc_with_bounds(y, [0.9, 0.6, 0.4, 0.2, 0.7, 0.5])
    assert full["lower"] == full["upper"] == full["auroc"] and full["coverage"] == 1.0
    part = auroc_with_bounds(y, [0.9, None, 0.4, None, 0.3, 0.5])
    assert part["n_available"] == 4
    assert part["lower"] <= part["upper"]
    # worst case: the unavailable Attack scored 0 and the unavailable Non-Attack scored 1
    assert part["lower"] == pytest.approx(auroc(y, [0.9, 0.0, 0.4, 1.0, 0.3, 0.5]))
    assert part["upper"] == pytest.approx(auroc(y, [0.9, 1.0, 0.4, 0.0, 0.3, 0.5]))


def test_bootstrap_is_seeded_and_stratified():
    groups = ["s1"] * 3 + ["s2"] * 5
    b1, b2 = bootstrap_indices(groups, n_boot=50), bootstrap_indices(groups, n_boot=50)
    assert (b1 == b2).all()
    assert all(set(r[:3]) <= {0, 1, 2} and set(r[3:]) <= {3, 4, 5, 6, 7} for r in b1)


def test_cluster_bootstrap_takes_whole_rules_within_rule_type():
    rules = ["r1", "r1", "r2", "r3", "r3", "r3"]
    types = ["mixed", "mixed", "mixed", "single", "single", "single"]
    for idx in cluster_bootstrap_indices(rules, types, n_boot=30):
        got = Counter(rules[i] for i in idx)
        assert got.get("r3", 0) in (0, 3, 6, 9) and got.get("r1", 0) in (0, 2, 4)
        assert sum(types[i] == "single" for i in idx) % 3 == 0


def test_paired_bootstrap_difference_uses_the_same_resamples():
    y = np.array([True] * 20 + [False] * 20)
    preds = {"good": np.where(y, 1, 0), "bad": np.where(y, 1, 1)}
    reps = bootstrap_indices(np.where(y, "a", "n"), n_boot=200)
    stat = lambda s, idx: float((preds[s][idx] == y[idx]).mean())  # noqa: E731
    out = paired_bootstrap(stat, ["good", "bad"], reps, n=len(y), pairs=[("good", "bad")])
    assert out["systems"]["good"]["point"] == 1.0 and out["systems"]["bad"]["point"] == 0.5
    d = out["differences"]["good - bad"]
    assert d["point"] == 0.5 and d["lo"] == d["hi"] == 0.5     # stratified by class: accuracy gap is fixed


def test_percentile_ci_reports_undefined_replicates():
    ci = percentile_ci([None, 1.0, 2.0, 3.0])
    assert ci["n_undefined"] == 1 and ci["lo"] >= 1.0 and ci["hi"] <= 3.0
