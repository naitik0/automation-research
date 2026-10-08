"""RQ3 held-out-rule folds on the shared sample (protocol §5) and the P15 fold report.

  python -m src.grouped_cv folds      # write manifests/rq3_folds.jsonl and print the P15 report
  python -m src.grouped_cv predict    # TF-IDF held-out predictions per condition -> results/rq3_tfidf.jsonl

Folds: StratifiedGroupKFold(5, shuffle=True, random_state=20261009), groups = rule_name, y = stratum, applied
to the shared-sample manifest in its file order. Only TF-IDF + logistic regression is trained (on the other
four folds); the LLMs are zero-shot and are scored later on the same held-out alerts.
"""
from __future__ import annotations

import argparse
import json
from collections import Counter

import numpy as np
from sklearn.model_selection import StratifiedGroupKFold

from .common import (CONDITIONS, MANIFESTS, RESULTS, SEED_FOLDS, STRATA, content_key, load_dataset, read_jsonl,
                     write_jsonl)
from .metrics import ATTACK, NON_ATTACK
from .references import tfidf_fit_score
from .tfidf_text import build_text

N_FOLDS = 5
FOLDS_PATH = MANIFESTS / "rq3_folds.jsonl"


def assign_folds(manifest: list[dict]) -> list[int]:
    sgkf = StratifiedGroupKFold(n_splits=N_FOLDS, shuffle=True, random_state=SEED_FOLDS)
    y = [r["stratum"] for r in manifest]
    groups = [r["rule_name"] for r in manifest]
    fold = [-1] * len(manifest)
    for k, (_, test) in enumerate(sgkf.split(np.zeros(len(manifest)), y, groups)):
        for i in test:
            fold[i] = k
    if -1 in fold:
        raise SystemExit("an alert was not assigned to a fold")
    return fold


def fold_rows(manifest: list[dict], fold: list[int]) -> list[dict]:
    """Alert -> fold lines, then rule -> fold lines (§5 step 1)."""
    alerts = [{"kind": "alert", "uid": r["uid"], "row_index": r["row_index"], "rule_name": r["rule_name"],
               "stratum": r["stratum"], "fold": k} for r, k in zip(manifest, fold)]
    rules = {}
    for a in alerts:
        rules.setdefault(a["rule_name"], set()).add(a["fold"])
    rule_rows = [{"kind": "rule", "rule_name": r, "folds": sorted(f),
                  "alerts": sum(a["rule_name"] == r for a in alerts)} for r, f in sorted(rules.items())]
    return alerts + rule_rows


def p15_report(manifest: list[dict], fold: list[int], data: list[dict]) -> dict:
    """§11 P15: per-fold counts; zero rule and content-key overlap between training and held-out folds."""
    keys = [content_key(data[r["row_index"]]) for r in manifest]
    per_fold, problems = [], []
    for k in range(N_FOLDS):
        held = [i for i, f in enumerate(fold) if f == k]
        train = [i for i, f in enumerate(fold) if f != k]
        held_rules = {manifest[i]["rule_name"] for i in held}
        train_rules = {manifest[i]["rule_name"] for i in train}
        rule_overlap = len(held_rules & train_rules)
        key_overlap = len({keys[i] for i in held} & {keys[i] for i in train})
        classes = Counter(manifest[i]["label"] for i in held)
        strata = Counter(manifest[i]["stratum"] for i in held)
        missing_class = [c for c in (ATTACK, NON_ATTACK) if classes[c] == 0]
        per_fold.append({"fold": k, "alerts": len(held), "rules": len(held_rules),
                         "attack": classes[ATTACK], "non_attack": classes[NON_ATTACK],
                         "strata": {h: strata[h] for h in STRATA}, "train_alerts": len(train),
                         "rule_overlap_with_train": rule_overlap, "content_key_overlap_with_train": key_overlap,
                         "missing_class": missing_class})
        if rule_overlap or key_overlap:
            problems.append(f"fold {k}: rule overlap {rule_overlap}, content-key overlap {key_overlap}")
    flags = [f"fold {p['fold']} lacks {', '.join(p['missing_class'])} (AUROC undefined there)"
             for p in per_fold if p["missing_class"]]
    held_once = sorted(Counter(fold).values())
    return {"pass": not problems and sum(held_once) == len(manifest), "problems": problems, "flags": flags,
            "alerts": len(manifest), "fold_sizes": [p["alerts"] for p in per_fold], "per_fold": per_fold}


def predict(manifest: list[dict], fold: list[int], data: list[dict]) -> list[dict]:
    """§5 step 2: for each fold and condition, fit on the other four folds and score the held-out fold."""
    out = [{"uid": r["uid"], "fold": k} for r, k in zip(manifest, fold)]
    y = np.array([r["label"] == ATTACK for r in manifest])
    for k in range(N_FOLDS):
        held = [i for i, f in enumerate(fold) if f == k]
        train = [i for i, f in enumerate(fold) if f != k]
        for cond in CONDITIONS:
            text = lambda i: build_text(data[manifest[i]["row_index"]], cond)  # noqa: E731
            p = tfidf_fit_score([text(i) for i in train], y[train], [text(i) for i in held])
            for i, pi in zip(held, p):
                out[i][f"tfidf_{cond}_score"] = float(pi)
                out[i][f"tfidf_{cond}"] = ATTACK if pi >= 0.5 else NON_ATTACK
    return out


def load_folds(manifest: list[dict]) -> list[int]:
    by_uid = {r["uid"]: r["fold"] for r in read_jsonl(FOLDS_PATH) if r["kind"] == "alert"}
    return [by_uid[r["uid"]] for r in manifest]


def main(argv=None) -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", choices=["folds", "predict"])
    a = ap.parse_args(argv)
    manifest = read_jsonl(MANIFESTS / "shared_sample.jsonl")
    data = load_dataset()
    if a.cmd == "folds":
        fold = assign_folds(manifest)
        write_jsonl(FOLDS_PATH, fold_rows(manifest, fold))
        print(json.dumps(p15_report(manifest, fold, data), indent=1, ensure_ascii=False))
    else:
        fold = load_folds(manifest)
        write_jsonl(RESULTS / "rq3_tfidf.jsonl", predict(manifest, fold, data))


if __name__ == "__main__":
    main()
