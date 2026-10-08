from src.grouped_cv import N_FOLDS, assign_folds, fold_rows, p15_report

from .conftest import fake_record


def _manifest(n_rules: int = 30):
    rows, data = [], []
    for i in range(n_rules * 4):
        rule = f"rule-{i % n_rules}"
        label = "Attack" if i % 3 else "Non-Attack"
        kind = "mixed" if i % n_rules < 10 else "single"
        data.append(fake_record(i, label, rule))
        rows.append({"uid": f"u{i:04d}", "row_index": i, "rule_name": rule, "label": label,
                     "stratum": f"{kind}_{'attack' if label == 'Attack' else 'non_attack'}"})
    return rows, data


def test_folds_are_deterministic_and_group_by_rule():
    m, data = _manifest()
    f1, f2 = assign_folds(m), assign_folds(m)
    assert f1 == f2 and set(f1) == set(range(N_FOLDS))
    by_rule = {}
    for r, k in zip(m, f1):
        by_rule.setdefault(r["rule_name"], set()).add(k)
    assert all(len(v) == 1 for v in by_rule.values())
    rep = p15_report(m, f1, data)
    assert rep["pass"] and sum(rep["fold_sizes"]) == len(m)
    assert all(p["rule_overlap_with_train"] == 0 and p["content_key_overlap_with_train"] == 0
               for p in rep["per_fold"])


def test_fold_rows_hold_alert_and_rule_maps():
    m, _ = _manifest()
    rows = fold_rows(m, assign_folds(m))
    assert sum(r["kind"] == "alert" for r in rows) == len(m)
    assert all(len(r["folds"]) == 1 for r in rows if r["kind"] == "rule")


def test_overlap_is_detected():
    m, data = _manifest()
    fold = assign_folds(m)
    fold[0] = (fold[0] + 1) % N_FOLDS                         # split one rule across two folds
    rep = p15_report(m, fold, data)
    assert not rep["pass"] and rep["problems"]
