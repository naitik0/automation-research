"""RQ1 reference baselines (protocol §4): always-Attack, the rule-identity reference and TF-IDF + logistic regression.

Out-of-sample: every test set is scored by references trained only on the frame alerts whose content key is
not in that test set. Test sets are the 15 published prediction files (all 2,000 rows as published, labels
from `true_label`, D7) and the shared sample (one TF-IDF fit per information condition).

Test input (D10): for a published file, each row's own published `record` (exactly what that published model was
shown) supplies the TF-IDF text and the rule name; training text always comes from pinned-dataset rows.
Published rows whose content key matches no dataset row stay in the test set and are flagged
(`matched_to_dataset` false); their count is recorded and reported as a limitation.

  python -m src.references check-splits         # sizes, matching and disjointness only; computes no metric
  python -m src.references predict --test <published model | shared>
      # writes results/rq1_refs_<test>.jsonl and results/rq1_refs_<test>.summary.json
"""
from __future__ import annotations

import argparse
import json
import warnings
from collections import Counter

import numpy as np
from sklearn.feature_extraction.text import HashingVectorizer, TfidfTransformer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import make_pipeline

from .common import (CONDITIONS, MANIFESTS, PUBLISHED_DIR, RESULTS, alert_uid, build_frame, content_key,
                     load_dataset, read_jsonl, write_json, write_jsonl)
from .metrics import ATTACK, NON_ATTACK
from .tfidf_text import build_text

# The 15 usable published per-alert files (§0; gemini-3-flash-preview is summary-only, D9).
PUBLISHED_MODELS = (
    "Foundation-Sec-8B-Instruct", "SecGPT-14B", "SecGPT-7B", "claude-sonnet-4-5-20250929", "deepseek-v3.1",
    "glm-4.7", "gpt-5.1-chat", "kimi-k2-instruct-0905", "llama-3.1-405b-instruct", "llama-3.1-70b-instruct",
    "llama-3.1-8b-instruct", "qwen3-14b", "qwen3-235b-a22b-instruct-2507", "qwen3-30b-a3b-instruct-2507",
    "qwen3-32b",
)


def load_published(model: str) -> tuple[list[dict], dict]:
    """All rows of one published file, as published. `record` is exactly what that LLM was shown."""
    d = json.load(open(PUBLISHED_DIR / f"{model}.json", encoding="utf-8"))
    rows = []
    for i, r in enumerate(d["results"]):
        key = content_key(r["record"])
        rows.append({"row": i, "key": key, "uid": alert_uid(key), "true_label": r["true_label"],
                     "llm_label": r["llm_label"] if r["llm_label"] in (ATTACK, NON_ATTACK) else None,
                     "rule_name": r["record"]["rule_name"], "record": r["record"]})
    return rows, d["summary"]


# ---- references --------------------------------------------------------------------------------------------

class RuleIdentity:
    """Diagnostic (§4): the rule's majority label in training; tie -> Attack; rule absent -> Non-Attack.
    Score: the rule's Attack share in training; for an absent rule, the overall training Attack rate."""

    def fit(self, rules, y_attack):
        n, a = Counter(rules), Counter(r for r, y in zip(rules, y_attack) if y)
        self.share = {r: a[r] / n[r] for r in n}
        self.base_rate = sum(a.values()) / len(rules)
        return self

    def score(self, rules) -> np.ndarray:
        return np.array([self.share.get(r, self.base_rate) for r in rules])

    def predict(self, rules) -> list[str]:
        return [NON_ATTACK if r not in self.share else (ATTACK if self.share[r] >= 0.5 else NON_ATTACK)
                for r in rules]


def tfidf_pipeline():
    """§4, fixed in advance with no tuning. `penalty="l2"` is the protocol's wording; scikit-learn 1.8 marks the
    argument deprecated (FutureWarning) but still applies it, identical to its default l1_ratio=0."""
    return make_pipeline(
        HashingVectorizer(analyzer="char", ngram_range=(3, 5), n_features=2 ** 20, alternate_sign=False,
                          norm=None, lowercase=False),
        TfidfTransformer(sublinear_tf=True),
        LogisticRegression(C=1.0, penalty="l2", solver="liblinear", class_weight="balanced", max_iter=1000,
                           random_state=0),
    )


def tfidf_fit_score(train_texts, train_attack, test_texts) -> np.ndarray:
    """p(Attack) for each test text; Attack if p >= 0.5."""
    with warnings.catch_warnings():
        warnings.filterwarnings("ignore", message="'penalty' was deprecated", category=FutureWarning)
        model = tfidf_pipeline().fit(train_texts, np.asarray(train_attack, dtype=int))
    classes = list(model.classes_)
    return model.predict_proba(test_texts)[:, classes.index(1)]


# ---- out-of-sample training sets ---------------------------------------------------------------------------

def frame_with_keys(data: list[dict]) -> list[dict]:
    frame, _ = build_frame(data)
    return [{**f, "key": content_key(data[f["row_index"]])} for f in frame]


def training_set(frame: list[dict], test_keys: set) -> list[dict]:
    """§4: frame alerts (deduplicated) whose content key is not in the test set."""
    return [f for f in frame if f["key"] not in test_keys]


def split_report(name: str, frame: list[dict], test_rows: list[dict], test_keys: set, data_keys: dict) -> dict:
    train = training_set(frame, test_keys)
    train_keys = {f["key"] for f in train}
    matched = [r for r in test_rows if r["key"] in data_keys]
    label_conflicts = sum(1 for r in matched if r["true_label"] not in data_keys[r["key"]])
    train_rules = {f["rule_name"] for f in train}
    return {
        "test_set": name, "test_rows": len(test_rows), "test_unique_keys": len(test_keys),
        "test_rows_unmatched_to_dataset": len(test_rows) - len(matched),
        "test_rows_label_conflict_with_dataset": label_conflicts,
        "train_alerts": len(train), "train_test_key_overlap": len(train_keys & test_keys),
        "train_attack": sum(f["label"] == ATTACK for f in train),
        "test_rules_absent_from_train": len({r["rule_name"] for r in test_rows} - train_rules),
        "test_rows_with_rule_absent_from_train": sum(r["rule_name"] not in train_rules for r in test_rows),
    }


def check_splits() -> dict:
    data = load_dataset()
    frame = frame_with_keys(data)
    data_keys: dict[str, set] = {}
    for r in data:
        data_keys.setdefault(content_key(r), set()).add(r["Label"])
    reports = []
    for m in PUBLISHED_MODELS:
        rows, _ = load_published(m)
        reports.append(split_report(m, frame, rows, {r["key"] for r in rows}, data_keys))
    shared = read_jsonl(MANIFESTS / "shared_sample.jsonl")
    rows = [{"key": content_key(data[s["row_index"]]), "true_label": s["label"], "rule_name": s["rule_name"]}
            for s in shared]
    reports.append(split_report("shared_sample", frame, rows, {r["key"] for r in rows}, data_keys))
    ok = all(r["train_test_key_overlap"] == 0 for r in reports)
    return {"pass": ok, "splits": reports}


# ---- predictions -------------------------------------------------------------------------------------------

def predict_test_set(frame: list[dict], data: list[dict], test_rows: list[dict], conditions) -> tuple[list, dict]:
    """Per-alert reference predictions for one test set, and a summary.

    test_rows need key, uid, rule_name and `record`: the alert as the LLM saw it (D10). Training uses pinned-dataset
    rows (frame alerts) whose content key is not in the test set.
    """
    train = training_set(frame, {r["key"] for r in test_rows})
    y = [f["label"] == ATTACK for f in train]
    ri = RuleIdentity().fit([f["rule_name"] for f in train], y)
    rules = [r["record"]["rule_name"] for r in test_rows]
    data_keys = {content_key(r) for r in data}
    out = [{"row": r.get("row"), "uid": r["uid"], "matched_to_dataset": r["key"] in data_keys,
            "always_attack": ATTACK, "rule_identity": p, "rule_identity_score": float(s),
            "rule_in_train": rule in ri.share}
           for r, rule, p, s in zip(test_rows, rules, ri.predict(rules), ri.score(rules))]
    summary = {"test_rows": len(out), "unmatched_to_dataset": sum(not o["matched_to_dataset"] for o in out),
               "train_alerts": len(train),
               "test_rows_with_rule_absent_from_train": sum(not o["rule_in_train"] for o in out)}
    for cond in conditions:
        p = tfidf_fit_score([build_text(data[f["row_index"]], cond) for f in train], y,
                            [build_text(r["record"], cond) for r in test_rows])
        for o, pi in zip(out, p):
            o[f"tfidf_{cond}_score"] = float(pi)
            o[f"tfidf_{cond}"] = ATTACK if pi >= 0.5 else NON_ATTACK
    return out, summary


def main(argv=None) -> None:
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("check-splits")
    p = sub.add_parser("predict")
    p.add_argument("--test", required=True, choices=[*PUBLISHED_MODELS, "shared"])
    a = ap.parse_args(argv)
    if a.cmd == "check-splits":
        print(json.dumps(check_splits(), indent=1, ensure_ascii=False))
        return
    data = load_dataset()
    frame = frame_with_keys(data)
    if a.test == "shared":
        rows = [{"row": i, "uid": s["uid"], "key": content_key(data[s["row_index"]]), "rule_name": s["rule_name"],
                 "record": data[s["row_index"]]} for i, s in enumerate(read_jsonl(MANIFESTS / "shared_sample.jsonl"))]
        conds = tuple(CONDITIONS)                      # one fit per information condition (§4)
    else:
        rows, _ = load_published(a.test)
        conds = ("a",)                                 # the published models all saw the full prompt
    out, summary = predict_test_set(frame, data, rows, conds)
    write_jsonl(RESULTS / f"rq1_refs_{a.test}.jsonl", out)
    write_json(RESULTS / f"rq1_refs_{a.test}.summary.json", {"test": a.test, "conditions": list(conds), **summary})
    print(json.dumps({"test": a.test, **summary}))


if __name__ == "__main__":
    main()
