"""Offline dry-run checks (protocol §11): P1, P2, P2b, P3, P11, P14, P15. No server, no API.

  python -m src.checks all          # or any of: P1 P2 P2b P3 P11 P14 P15
Each report is written to runs/dryrun/checks/<check>.json. Reports hold counts, hashes and rule names only,
never alert content.
"""
from __future__ import annotations

import ast
import json
import re
import sys
import tempfile
import typing
import unicodedata
from collections import Counter
from pathlib import Path

import numpy as np

from .common import (BENCH_SCRIPT, CONDITIONS, DRYRUN_PER_STRATUM, MANIFESTS, MAX_PROMPT_TOKENS,
                     PRODUCTION_PER_STRATUM, RUNS, STRATA, load_dataset, read_jsonl, sha256_file, write_json)
from .metrics import auroc, counts, encode, from_counts

REPORTS = RUNS / "dryrun" / "checks"
HEADER = "Alert fields (JSON):\n"
# §1 table (no length exclusions): frame and post-dry-run stratum sizes, class-balanced weights to 4 dp.
PROTOCOL_FRAME = {"mixed_attack": 906, "single_attack": 1503, "mixed_non_attack": 2536, "single_non_attack": 3259}
PROTOCOL_WEIGHTS = {"mixed_attack": 0.7501, "single_attack": 1.2499, "mixed_non_attack": 0.8748,
                    "single_non_attack": 1.1252}


def _samples() -> list[dict]:
    return read_jsonl(MANIFESTS / "dryrun_sample.jsonl") + read_jsonl(MANIFESTS / "shared_sample.jsonl")


def _bench_function(name: str):
    """One function from the pinned benchmark script: only its own `def` node is compiled, never the module, so
    no other downloaded code runs. Its source is asserted identical to the pinned text (prompts.py)."""
    from .prompts import VALID_LABELS, _bench_ast
    _, tree = _bench_ast()
    nodes = [n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == name]
    ns = {"json": json, "Any": typing.Any, "VALID_LABELS": VALID_LABELS}
    exec(compile(ast.Module(body=nodes, type_ignores=[]), str(BENCH_SCRIPT), "exec"), ns)  # noqa: S102
    return ns[name]


def p1() -> dict:
    """Sampling reproducibility: two builds from scratch are byte-identical to each other and to the manifests."""
    from .sample import build
    files = ("dryrun_sample.jsonl", "shared_sample.jsonl", "sample_summary.json")
    with tempfile.TemporaryDirectory() as d1, tempfile.TemporaryDirectory() as d2:
        build(Path(d1))
        build(Path(d2))
        same_runs = {f: (Path(d1) / f).read_bytes() == (Path(d2) / f).read_bytes() for f in files}
        same_committed = {f: (Path(d1) / f).read_bytes() == (MANIFESTS / f).read_bytes() for f in files}
        dry, prod = read_jsonl(Path(d1) / files[0]), read_jsonl(Path(d1) / files[1])
        summary = json.loads((Path(d1) / files[2]).read_text(encoding="utf-8"))
    dry_n, prod_n = Counter(r["stratum"] for r in dry), Counter(r["stratum"] for r in prod)
    checks = {
        "byte_identical_between_builds": all(same_runs.values()),
        "byte_identical_to_manifests": all(same_committed.values()),
        "dryrun_strata_exact": all(dry_n[h] == DRYRUN_PER_STRATUM for h in STRATA),
        "production_strata_exact": all(prod_n[h] == PRODUCTION_PER_STRATUM for h in STRATA),
        "no_dryrun_alert_in_production": not ({r["uid"] for r in dry} & {r["uid"] for r in prod}),
        "no_uid_repeats": len({r["uid"] for r in dry + prod}) == len(dry) + len(prod),
        "frame_strata_match_protocol_table": summary["frame_per_stratum"] == PROTOCOL_FRAME,
        "weights_match_protocol_table": all(round(summary["weights"][h], 4) == PROTOCOL_WEIGHTS[h] for h in STRATA),
        "length_exclusions": summary["excluded_too_long"],
    }
    ok = all(v for k, v in checks.items() if k != "length_exclusions")
    return {"pass": ok, **checks, "per_file_between_builds": same_runs, "per_file_vs_manifests": same_committed,
            "manifest_sha256": {f: sha256_file(MANIFESTS / f) for f in files[:2]},
            "note": "token lengths for the §1 length check are read from manifests/token_lengths_frame_*.jsonl"}


def p2() -> dict:
    """Prompt fidelity for all 1,040 sampled alerts (dry run + production)."""
    from .prompts import (SYSTEM_PROMPT, SYSTEM_SHA256, benchmark_system_prompt, check_benchmark_sources,
                          parse_label, user_message)
    bench_build = _bench_function("build_user_content")
    bench_parse = _bench_function("parse_label")
    data = load_dataset()
    rows = _samples()
    fails = Counter()
    for r in rows:
        rec = data[r["row_index"]]
        bench_record = {k: v for k, v in rec.items() if k != "Label"}
        a = user_message(rec, "a")
        if a != bench_build(bench_record):
            fails["a_differs_from_benchmark_build_user_content"] += 1
        keys_a = list(json.loads(a[len(HEADER):]).keys())
        for cond in ("b", "c"):
            msg = user_message(rec, cond)
            if not msg.startswith(HEADER):
                fails[f"{cond}_header"] += 1
                continue
            got = json.loads(msg[len(HEADER):])
            want_keys = [k for k in keys_a if k not in CONDITIONS[cond]]
            if list(got.keys()) != want_keys or any(got[k] != bench_record[k] for k in want_keys):
                fails[f"{cond}_not_a_minus_removed_keys"] += 1
    parse_cases = ["Attack", " Non-Attack\n", "Non-Attack.", "attack", "The answer: Attack", "", None,
                   "Non-Attack or Attack", "NON-ATTACK", "Attack Non-Attack", "Benign"]
    parse_same = all(parse_label(x) == bench_parse(x) for x in parse_cases)
    sources = check_benchmark_sources()
    system_ok = SYSTEM_PROMPT == benchmark_system_prompt()
    ok = not fails and parse_same and all(sources.values()) and system_ok
    return {"pass": ok, "alerts": len(rows), "failures": dict(fails), "system_prompt_equal": system_ok,
            "system_sha256": SYSTEM_SHA256, "benchmark_sources_identical": sources,
            "parser_matches_benchmark_on_cases": parse_same,
            "note": "benchmark functions compiled from their own AST nodes only; the benchmark module is never run"}


def _reference_text(rec: dict, cond: str) -> str:
    """Independent re-implementation of §4.1 (dataset key order, regex line endings) for the P2b comparison."""
    vals = []
    for field, v in rec.items():
        if field == "Label" or field in CONDITIONS[cond]:
            continue
        v = "" if v is None else (str(v) if isinstance(v, int) and not isinstance(v, bool) else v)
        vals.append(re.sub(r"\r\n?", "\n", unicodedata.normalize("NFC", v)))
    return "\n".join(vals).lower()


def p2b() -> dict:
    from .prompts import SYSTEM_PROMPT
    from .tfidf_text import build_text
    data = load_dataset()
    rows = _samples()
    differ, constant = Counter(), Counter()
    attack_word = {c: Counter() for c in CONDITIONS}
    types = Counter(type(v).__name__ for r in rows for k, v in data[r["row_index"]].items() if k != "Label")
    for r in rows:
        rec = data[r["row_index"]]
        for cond in CONDITIONS:
            t = build_text(rec, cond)
            if t != _reference_text(rec, cond):
                differ[cond] += 1
            if SYSTEM_PROMPT.strip().lower() in t or HEADER.strip().lower() in t:
                constant[cond] += 1
            if "attack" in t:
                attack_word[cond][r["label"]] += 1
    ok = not differ and not constant
    return {"pass": ok, "alerts": len(rows), "texts": len(rows) * len(CONDITIONS),
            "differs_from_reference_construction": dict(differ), "contains_constant_prompt_text": dict(constant),
            "value_types": dict(types),
            "alerts_whose_own_values_contain_attack": {c: dict(v) for c, v in attack_word.items()},
            "note": "field names never enter the text by construction (values only, joined by newline); "
                    "the equality with an independent construction checks this"}


def p3() -> dict:
    out, ok = {}, True
    want = {r["uid"] for r in _samples()}
    for m in ("qwen3-4b", "llama-3.2-3b"):
        path = MANIFESTS / f"token_lengths_samples_{m}.jsonl"
        if not path.exists():
            out[m] = {"missing": str(path.name)}
            ok = False
            continue
        rows = read_jsonl(path)
        mx = {c: max(r[f"tokens_{c}"] for r in rows) for c in CONDITIONS}
        over = sum(1 for r in rows for c in CONDITIONS if r[f"tokens_{c}"] > MAX_PROMPT_TOKENS)
        frame = read_jsonl(MANIFESTS / f"token_lengths_frame_{m}.jsonl")
        out[m] = {"sample_alerts": len(rows), "uids_match_samples": {r["uid"] for r in rows} == want,
                  "max_tokens": mx, "prompts_over_limit": over,
                  "frame_alerts": len(frame), "frame_max_tokens_a": max(r["tokens_a"] for r in frame),
                  "frame_over_limit": sum(r["tokens_a"] > MAX_PROMPT_TOKENS for r in frame)}
        ok &= out[m]["uids_match_samples"] and over == 0 and out[m]["frame_over_limit"] == 0
    return {"pass": ok, "limit": MAX_PROMPT_TOKENS, **out}


def p11() -> dict:
    from .references import PUBLISHED_MODELS, load_published
    files, ok = {}, True
    for m in PUBLISHED_MODELS:
        rows, summary = load_published(m)
        t, p = encode([r["true_label"] for r in rows], [r["llm_label"] for r in rows])
        c = counts(t, p, invalid="exclude")              # the benchmark's convention (valid responses only)
        mt = from_counts(c)
        s = summary["metrics"]
        got = {"TP": int(c["TP"]), "FP": int(c["FP"]), "TN": int(c["TN"]), "FN": int(c["FN"])}
        match = {
            "confusion": got == s["confusion_matrix"],
            "f1": round(mt["f1"], 6) == s["f1_score"],
            "precision": round(mt["precision"], 6) == s["precision"],
            "tpr": round(mt["tpr"], 6) == s["recall_tpr"],
            "fpr": round(mt["fpr"], 6) == s["fpr"],
            "valid_eval_count": c["n"] == s["valid_eval_count"],
        }
        files[m] = {"all_match": all(match.values()), **({} if all(match.values()) else {"detail": match})}
        ok &= all(match.values())
    # Hand-computed case: TP=3 FP=1 TN=2 FN=2, one invalid Attack (counts as FN under the primary convention).
    yt = ["Attack"] * 6 + ["Non-Attack"] * 3
    yp = ["Attack", "Attack", "Attack", "Non-Attack", "Non-Attack", None, "Attack", "Non-Attack", "Non-Attack"]
    tt, pp = encode(yt, yp)
    hand = counts(tt, pp) == {"TP": 3.0, "FP": 1.0, "TN": 2.0, "FN": 3.0, "n": 9, "n_invalid": 1} and \
        counts(tt, pp, invalid="exclude")["FN"] == 2.0
    # AUROC against scikit-learn on random scores with heavy ties, unweighted and weighted.
    from sklearn.metrics import roc_auc_score
    g = np.random.Generator(np.random.PCG64(0))
    worst = 0.0
    for _ in range(200):
        n = int(g.integers(5, 300))
        y = g.integers(0, 2, n).astype(bool)
        if y.all() or not y.any():
            continue
        sc = g.integers(0, 6, n) / 5.0
        w = g.uniform(0.5, 1.5, n)
        worst = max(worst, abs(auroc(y, sc) - roc_auc_score(y, sc)),
                    abs(auroc(y, sc, w) - roc_auc_score(y, sc, sample_weight=w)))
    ok &= hand and worst < 1e-12
    return {"pass": ok, "published_files": len(files), "files": files, "hand_computed_case": hand,
            "auroc_max_abs_diff_vs_sklearn": worst}


def p14() -> dict:
    from .sample import concentration
    shared = read_jsonl(MANIFESTS / "shared_sample.jsonl")
    rep = concentration(shared)
    stored = json.loads((MANIFESTS / "sample_summary.json").read_text(encoding="utf-8"))
    same = rep == stored["p14_concentration_shared_sample"]
    return {"pass": same, "informational": True, "matches_sample_summary": same, **rep}


def p15() -> dict:
    from .grouped_cv import FOLDS_PATH, assign_folds, load_folds, p15_report
    manifest = read_jsonl(MANIFESTS / "shared_sample.jsonl")
    fold = assign_folds(manifest)
    reproducible = FOLDS_PATH.exists() and load_folds(manifest) == fold
    rep = p15_report(manifest, fold, load_dataset())
    return {**rep, "pass": rep["pass"] and reproducible, "matches_saved_folds": reproducible,
            "folds_sha256": sha256_file(FOLDS_PATH) if FOLDS_PATH.exists() else None}


CHECKS = {"P1": p1, "P2": p2, "P2b": p2b, "P3": p3, "P11": p11, "P14": p14, "P15": p15}


def main(argv=None) -> int:
    names = (argv if argv is not None else sys.argv[1:]) or ["all"]
    if names == ["all"]:
        names = list(CHECKS)
    failed = []
    for name in names:
        rep = {"check": name, **CHECKS[name]()}
        write_json(REPORTS / f"{name}.json", rep)
        print(f"{name}: {'PASS' if rep['pass'] else 'FAIL'}")
        if not rep["pass"]:
            failed.append(name)
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
