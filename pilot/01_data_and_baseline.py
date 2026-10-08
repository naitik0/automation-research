"""Pilot criteria 1 and 2 (SecAlertBench): data matching and rule-majority baseline.

Run from the repo root:  python -X utf8 -P pilot/01_data_and_baseline.py
Writes pilot/results/01_data_and_baseline.json and prints a summary.

Everything is deterministic (fixed seeds). Needs only the standard library + numpy.
"""
import json
import random
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent
DATA = ROOT / "data" / "secalertbench"
OUT = ROOT / "results" / "01_data_and_baseline.json"
SEEDS = (0, 1, 2)
# gemini-3-flash-preview.json is removed by Windows Defender when saved to disk (exploit payloads in the alerts), so
# its in-file `summary.metrics` was read from the first 2.5 KB of the raw GitHub file (no payload in that range):
GEMINI_SUMMARY = {"f1_score": 0.871011, "recall_tpr": 0.969, "fpr": 0.256}
LLM_REPORTED = {"avg_f1": 0.7092, "avg_tpr": 0.7971, "avg_fpr": 0.4413}  # SecAlertBench abstract


# The released prediction files were produced on records whose IP addresses differ from the released
# dataset (the README says IPs were replaced with random ones), so records are matched on everything
# except the IP-bearing fields.
IP_FIELDS = {"sip", "dip", "xff"}


def key(rec):
    """Canonical content key of an alert record (the dataset adds `Label`; prediction files don't)."""
    return json.dumps({k: v for k, v in rec.items() if k != "Label" and k not in IP_FIELDS},
                      sort_keys=True, ensure_ascii=False)


def metrics(y, p, w=None):
    """TPR, FPR, precision, F1 with positive class = Attack (1). Optional per-sample weights."""
    y, p = np.asarray(y), np.asarray(p)
    w = np.ones(len(y)) if w is None else np.asarray(w, dtype=float)
    tp = w[(y == 1) & (p == 1)].sum()
    fp = w[(y == 0) & (p == 1)].sum()
    fn = w[(y == 1) & (p == 0)].sum()
    tn = w[(y == 0) & (p == 0)].sum()
    tpr = tp / (tp + fn) if tp + fn else 0.0
    fpr = fp / (fp + tn) if fp + tn else 0.0
    prec = tp / (tp + fp) if tp + fp else 0.0
    f1 = 2 * prec * tpr / (prec + tpr) if prec + tpr else 0.0
    return {"tpr": tpr, "fpr": fpr, "precision": prec, "f1": f1}


def rule_majority(train_rules, train_y, test_rules, fallback):
    """Predict each rule's majority training label (ties -> Attack); unseen rule -> fallback."""
    cnt = defaultdict(lambda: [0, 0])
    for r, y in zip(train_rules, train_y):
        cnt[r][y] += 1
    table = {r: int(c[1] >= c[0]) for r, c in cnt.items()}
    return np.array([table.get(r, fallback) for r in test_rules]), np.array([r in table for r in test_rules])


def main():
    report = {}
    data = json.load(open(DATA / "secalertbench.json", encoding="utf-8"))
    n = len(data)
    y_all = np.array([1 if r["Label"] == "Attack" else 0 for r in data])
    rules_all = [r["rule_name"] for r in data]
    keys = [key(r) for r in data]
    key_count = Counter(keys)
    report["dataset"] = {
        "n": n, "attack": int(y_all.sum()), "non_attack": int((1 - y_all).sum()),
        "n_rules": len(set(rules_all)),
        "duplicate_record_keys": int(sum(1 for c in key_count.values() if c > 1)),
        "records_in_duplicate_groups": int(sum(c for c in key_count.values() if c > 1)),
    }
    by_rule = defaultdict(lambda: [0, 0])
    for r, y in zip(rules_all, y_all):
        by_rule[r][y] += 1
    single = [r for r, c in by_rule.items() if min(c) == 0]
    mixed_rules = [r for r, c in by_rule.items() if min(c) > 0]
    report["rules"] = {
        "single_label_rules": len(single), "mixed_label_rules": len(mixed_rules),
        "alerts_in_mixed_rules": int(sum(sum(by_rule[r]) for r in mixed_rules)),
    }
    index = {}
    for i, k in enumerate(keys):
        index.setdefault(k, []).append(i)

    # ---- Criterion 2: match every model's prediction file to dataset rows ----
    models = {}
    pred_rows = {}  # model -> {content key -> (true_label_int, pred_int or None, rule_name)}
    model_exclude = {}  # model -> dataset rows content-identical to an alert that model was evaluated on
    for f in sorted((DATA / "rq1").glob("*.json")):
        d = json.load(open(f, encoding="utf-8"))
        res = d["results"]
        unmatched = ambiguous = label_conflict = rule_conflict = 0
        rows = {}
        ex = set()
        for row in res:
            k = key(row["record"])
            idx = index.get(k)
            t = 1 if row["true_label"] == "Attack" else 0
            if not idx:
                unmatched += 1
            else:
                if len(idx) > 1:
                    ambiguous += 1
                if any(int(y_all[i]) != t for i in idx):
                    label_conflict += 1
                if any(rules_all[i] != row["record"]["rule_name"] for i in idx):
                    rule_conflict += 1
                ex.update(idx)
            pl = row["llm_label"]
            rows[k] = (t, None if pl not in ("Attack", "Non-Attack") else int(pl == "Attack"), row["record"]["rule_name"])
        valid = [(t, p) for t, p, _ in rows.values() if p is not None]
        m = metrics([t for t, _ in valid], [p for _, p in valid])
        s_ = d["summary"]["metrics"]
        models[f.stem] = {
            "rows": len(res), "unique_content_keys": len(rows), "unmatched_to_dataset": unmatched,
            "matched_but_ambiguous_duplicates": ambiguous, "matched_with_label_conflict": label_conflict,
            "matched_with_rule_conflict": rule_conflict,
            "invalid_llm_outputs": len(rows) - len(valid),
            "recomputed": m, "reported_in_file_summary": {k_: s_.get(k_) for k_ in ("precision", "recall_tpr", "f1_score", "fpr")},
        }
        pred_rows[f.stem] = rows
        model_exclude[f.stem] = ex
    report["models"] = models
    keysets = [set(r) for r in pred_rows.values()]
    inter_keys = set.intersection(*keysets)
    first = next(iter(pred_rows))
    report["eval_sample"] = {
        "models": len(models), "keys_in_all_models": len(inter_keys), "keys_in_any_model": len(set.union(*keysets)),
        "overlap_with_first_model": {m: len(set(pred_rows[m]) & set(pred_rows[first])) for m in pred_rows},
        "first_model": first,
        "note": "each model was scored on its own random 2,000-alert sample (--sample-per-class 1000, balanced)",
    }
    report["llm_average_recomputed"] = {
        k_: float(np.mean([m["recomputed"][k_] for m in models.values()])) for k_ in ("f1", "tpr", "fpr")
    }
    fs = [m["reported_in_file_summary"] for m in models.values()]
    report["llm_average_from_file_summaries_15_models"] = {
        "f1": float(np.mean([x["f1_score"] for x in fs])), "tpr": float(np.mean([x["recall_tpr"] for x in fs])),
        "fpr": float(np.mean([x["fpr"] for x in fs]))}
    fs16 = fs + [GEMINI_SUMMARY]
    report["llm_average_from_file_summaries_16_models_incl_gemini"] = {
        "f1": float(np.mean([x["f1_score"] for x in fs16])), "tpr": float(np.mean([x["recall_tpr"] for x in fs16])),
        "fpr": float(np.mean([x["fpr"] for x in fs16]))}
    report["llm_average_reported_in_abstract"] = LLM_REPORTED

    # ---- Criterion 1: rule-majority baseline, scored on each model's own evaluation sample ----
    # Train on all dataset rows except those content-identical to that model's test alerts; unseen rule -> Non-Attack.
    fallback = 0
    mixed_set = set(mixed_rules)
    per_model_base, per_model_mixed = {}, {}
    for name, rows in pred_rows.items():
        test_keys = sorted(rows)
        yt = np.array([rows[k][0] for k in test_keys])
        test_rules = [rows[k][2] for k in test_keys]
        train_idx = np.array([i for i in range(n) if i not in model_exclude[name]])
        pred, seen = rule_majority([rules_all[i] for i in train_idx], y_all[train_idx], test_rules, fallback)
        bm = metrics(yt, pred)
        bm.update({"n_test": len(yt), "test_attack": int(yt.sum()), "n_train": int(len(train_idx)),
                   "test_alerts_with_unseen_rule": int((~seen).sum())})
        per_model_base[name] = bm
        mask = np.array([r in mixed_set for r in test_rules])
        llm_p = np.array([rows[k][1] if rows[k][1] is not None else -1 for k in test_keys])
        ok = mask & (llm_p >= 0)
        per_model_mixed[name] = {
            "n": int(ok.sum()), "baseline": metrics(yt[ok], pred[ok]), "llm": metrics(yt[ok], llm_p[ok])}
    avg = lambda d, f=lambda v: v: {k_: float(np.mean([f(v)[k_] for v in d.values()])) for k_ in ("f1", "tpr", "fpr")}
    report["baseline_per_model_sample"] = per_model_base
    report["baseline_average_over_model_samples"] = avg(per_model_base)
    report["mixed_rules_slice"] = {
        "average_n": float(np.mean([v["n"] for v in per_model_mixed.values()])),
        "baseline_average": avg(per_model_mixed, lambda v: v["baseline"]),
        "llm_average": avg(per_model_mixed, lambda v: v["llm"]),
    }
    # bootstrap CI for the mean baseline F1 (resample alerts within each model's sample)
    rng = np.random.default_rng(0)
    boots = []
    for _ in range(300):
        f1s = []
        for name, rows in pred_rows.items():
            test_keys = sorted(rows)
            yt = np.array([rows[k][0] for k in test_keys])
            # reuse stored baseline predictions via rule lookup on the full-train table is equivalent; recompute cheaply
            test_rules = [rows[k][2] for k in test_keys]
            tr = np.array([i for i in range(n) if i not in model_exclude[name]])
            pr, _ = rule_majority([rules_all[i] for i in tr], y_all[tr], test_rules, fallback)
            b = rng.integers(0, len(yt), len(yt))
            f1s.append(metrics(yt[b], pr[b])["f1"])
        boots.append(np.mean(f1s))
    report["baseline_average_f1_bootstrap_95ci"] = [float(np.percentile(boots, 2.5)), float(np.percentile(boots, 97.5))]
    # Full-set 5-fold CV x 3 seeds, plain and prevalence-balanced (reweight to 50/50 like the LLM test set)
    def cv(group_by_rule):
        out = []
        for seed in SEEDS:
            rr = random.Random(seed)
            if group_by_rule:
                ur = sorted(set(rules_all))
                rr.shuffle(ur)
                fold_of_rule = {r: i % 5 for i, r in enumerate(ur)}
                folds = np.array([fold_of_rule[r] for r in rules_all])
            else:
                perm = list(range(n))
                rr.shuffle(perm)
                folds = np.empty(n, dtype=int)
                for pos, i in enumerate(perm):
                    folds[i] = pos % 5
            P = np.zeros(n, dtype=int)
            for k in range(5):
                tr, te = np.where(folds != k)[0], np.where(folds == k)[0]
                P[te], _ = rule_majority([rules_all[i] for i in tr], y_all[tr], [rules_all[i] for i in te], fallback)
            pos_w = 0.5 / y_all.mean()
            neg_w = 0.5 / (1 - y_all.mean())
            w = np.where(y_all == 1, pos_w, neg_w)
            out.append({"plain": metrics(y_all, P), "balanced_f1": metrics(y_all, P, w)["f1"]})
        agg = {k: float(np.mean([o["plain"][k] for o in out])) for k in ("tpr", "fpr", "precision", "f1")}
        agg["balanced_f1"] = float(np.mean([o["balanced_f1"] for o in out]))
        return agg
    report["baseline_cv5_random_full_set"] = cv(False)
    report["baseline_cv5_grouped_by_rule_full_set"] = cv(True)
    OUT.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
    print(json.dumps({k: report[k] for k in report if k != "models"}, indent=2, ensure_ascii=False))
    print("\nper-model recomputed vs reported (f1 / fpr):")
    for m, v in models.items():
        print(f"  {m:32s} rows={v['rows']} keys={v['unique_content_keys']} unmatched={v['unmatched_to_dataset']} "
              f"ambig={v['matched_but_ambiguous_duplicates']} lblconf={v['matched_with_label_conflict']} "
              f"f1={v['recomputed']['f1']:.4f} (file {v['reported_in_file_summary']['f1_score']}) "
              f"fpr={v['recomputed']['fpr']:.4f} (file {v['reported_in_file_summary']['fpr']})")


if __name__ == "__main__":
    main()
