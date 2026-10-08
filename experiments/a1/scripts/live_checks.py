"""Dry-run checks that need a running llama-server or finished runs (protocol §11): P4, P5, and the per-model
P7/P8/P9/P13 report. Kept outside src/ so adding it does not change the locked harness.

  python scripts/live_checks.py p4 --model qwen3-4b       # re-render prompts: /apply-template only, no generation
  python scripts/live_checks.py p5 --model qwen3-4b       # 20 pilot-style /v1/chat/completions calls (generation)
  python scripts/live_checks.py report --model qwen3-4b   # P7, P8, P9, P13 from runs/dryrun/<model>/{final,p9}

Reports go to runs/dryrun/checks/<model>_<check>.json. No performance metric is computed.
"""
from __future__ import annotations

import argparse
import json
import re
import statistics
import sys
import time
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.common import MANIFESTS, RUNS, load_dataset, read_jsonl, sha256_text, write_json  # noqa: E402
from src.lock import harness_hash  # noqa: E402
from src.lock import load as load_lock  # noqa: E402
from src.models import MODELS, LocalClient  # noqa: E402
from src.prompts import SYSTEM_PROMPT, messages, parse_label, user_message  # noqa: E402
from src.run_llm import call_order  # noqa: E402

CHECKS = RUNS / "dryrun" / "checks"
DATE_RE = re.compile(r"\d{1,2} [A-Z][a-z]{2} \d{4}|\d{4}-\d{2}-\d{2}|today|date", re.IGNORECASE)
# The pilot's request (pilot/03_throughput_qwen3_4b.py): benchmark messages, temperature 0, max_tokens 8.
PILOT_BODY = {"temperature": 0, "max_tokens": 8, "stream": False}
P5_ALERTS = 20


def _run(model: str, subdir: str) -> list[dict]:
    return read_jsonl(RUNS / "dryrun" / model / subdir / "calls.jsonl")


def _server(model: str) -> LocalClient:
    c = LocalClient()
    if not str(c.props().get("model_path")).endswith(MODELS[model]["gguf"]):
        raise SystemExit(f"server is not running {model}")
    return c


def p4(model: str) -> dict:
    """Template stability: re-rendering every prompt of the finished run gives the recorded hash, and the
    template's own text (prompt minus the two messages) holds no date or run-varying text."""
    c, kw = _server(model), MODELS[model]["template_kwargs"] or None
    data = load_dataset()
    calls = _run(model, "final")
    manifest = {r["uid"]: r for r in read_jsonl(MANIFESTS / "dryrun_sample.jsonl")}
    differ = 0
    for x in calls:
        rec = data[manifest[x["alert_uid"]]["row_index"]]
        if sha256_text(c.apply_template(messages(rec, x["condition"]), kw)) != x["rendered_prompt_sha256"]:
            differ += 1
    probe = [{"role": "system", "content": "SYSTEM-PROBE"}, {"role": "user", "content": "USER-PROBE"}]
    renders = [c.apply_template(probe, kw) for _ in range(2)]
    scaffold = renders[0].replace("SYSTEM-PROBE", "").replace("USER-PROBE", "")
    hits = DATE_RE.findall(scaffold)
    ok = differ == 0 and renders[0] == renders[1] and not hits
    return {"pass": ok, "prompts_rerendered": len(calls), "hash_differs": differ,
            "probe_renders_identical": renders[0] == renders[1], "template_scaffold": scaffold,
            "date_like_text_in_scaffold": hits, "template_kwargs": kw}


def p5(model: str) -> dict:
    """Endpoint equivalence: for the first 20 dry-run alerts in call order, condition (a), the pilot's
    /v1/chat/completions label equals the label the run obtained via /apply-template + /completion."""
    c = _server(model)
    data = load_dataset()
    final = {(x["alert_uid"], x["condition"]): x for x in _run(model, "final")}
    alerts = [m for m, cond in call_order(read_jsonl(MANIFESTS / "dryrun_sample.jsonl")) if cond == "a"][:P5_ALERTS]
    out_dir = RUNS / "dryrun" / model / "p5"
    out_dir.mkdir(parents=True, exist_ok=True)
    rows = []
    for m in alerts:
        rec = data[m["row_index"]]
        body = {"messages": [{"role": "system", "content": SYSTEM_PROMPT},
                             {"role": "user", "content": user_message(rec, "a")}], **PILOT_BODY}
        t0 = time.time()
        r = c._post("/v1/chat/completions", body)
        text = r["choices"][0]["message"]["content"]
        ref = final[(m["uid"], "a")]
        rows.append({"alert_uid": m["uid"], "chat_raw": text, "chat_label": parse_label(text),
                     "completion_label": ref["parsed_label"], "completion_raw": ref["raw_text"],
                     "match": parse_label(text) == ref["parsed_label"], "latency_s": time.time() - t0,
                     "finish_reason": r["choices"][0].get("finish_reason")})
    with open(out_dir / "p5_calls.jsonl", "w", encoding="utf-8", newline="\n") as f:
        for row in rows:
            f.write(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n")
    n_match = sum(r["match"] for r in rows)
    return {"pass": n_match == len(rows), "alerts": len(rows), "labels_equal": n_match,
            "mismatches": [r["alert_uid"] for r in rows if not r["match"]],
            "chat_raw_outputs": dict(Counter(r["chat_raw"] for r in rows)),
            "pilot_request": PILOT_BODY, "harness": harness_hash()}


def report(model: str) -> dict:
    """P7 validity, P8 score extraction, P9 determinism and P13 timing from the finished runs."""
    lock = load_lock()
    calls = _run(model, "final")
    meta = json.loads((RUNS / "dryrun" / model / "final" / "run_meta.json").read_text(encoding="utf-8"))
    lt = meta["label_tokens"]
    cells = {}
    for key, sel in [(f"condition_{c}", lambda x, c=c: x["condition"] == c) for c in "abc"] + \
                    [(h, lambda x, h=h: x["stratum"] == h) for h in sorted({x["stratum"] for x in calls})]:
        cc = [x for x in calls if sel(x)]
        cells[key] = {"calls": len(cc), "invalid": sum(x["status"] == "invalid" for x in cc),
                      "invalid_rate": sum(x["status"] == "invalid" for x in cc) / len(cc),
                      "score_available": sum(x["score_available"] for x in cc),
                      "score_coverage": sum(x["score_available"] for x in cc) / len(cc)}
    p7 = all(cells[f"condition_{c}"]["invalid_rate"] <= 0.10 for c in "abc")
    coverage_gate = MODELS[model]["auroc"]                    # D11: Qwen3-4B coverage is a diagnostic, not a gate
    p8 = lt["prompt_prefix_unchanged"] and {k: lock["label_tokens"][model][k] for k in lt} == lt and \
        (not coverage_gate or all(cells[f"condition_{c}"]["score_coverage"] >= 0.95 for c in "abc"))
    first = Counter(str(x["generated_token_ids"][0]) if x["generated_token_ids"] else "none" for x in calls)
    reasons = Counter(x["score_unavailable_reason"] for x in calls if not x["score_available"])

    p9 = None
    p9_path = RUNS / "dryrun" / model / "p9" / "calls.jsonl"
    if p9_path.exists():
        base = {x["call_id"]: x for x in calls}
        rep = read_jsonl(p9_path)
        pairs = [(x, base[x["call_id"]]) for x in rep if x["call_id"] in base]
        same_label = sum(a["parsed_label"] == b["parsed_label"] for a, b in pairs)
        ds = [abs(a["score_attack"] - b["score_attack"]) for a, b in pairs
              if a["score_available"] and b["score_available"]]
        avail_same = sum(a["score_available"] == b["score_available"] for a, b in pairs)
        p9 = {"repeats": len(rep), "paired": len(pairs), "identical_labels": same_label,
              "score_availability_identical": avail_same, "scores_compared": len(ds),
              "max_abs_delta_score": max(ds) if ds else None,
              "pass": len(pairs) == 20 and same_label == 20 and avail_same == 20 and (not ds or max(ds) < 1e-3)}

    lat = [x["latency_s"] for x in calls]
    pt = [x["usage"]["prompt_tokens"] for x in calls]
    return {
        "P7": {"pass": p7, "limit": 0.10},
        "P8": {"pass": p8, "threshold": 0.95, "coverage_gate_applies": coverage_gate,
               "auroc_reported": MODELS[model]["auroc"],
               "label_tokens": {k: lt[k] for k in ("A", "A_pieces", "N", "N_pieces")},
               "k": lt["k"], "prompt_prefix_unchanged": lt["prompt_prefix_unchanged"],
               "label_tokens_match_lock": {k: lock["label_tokens"][model][k] for k in lt} == lt,
               "first_generated_token_ids": dict(first), "unavailable_reasons": dict(reasons)},
        "cells": cells,
        "P9": p9,
        "P13_inputs": {"calls": len(calls), "latency_mean_s": statistics.mean(lat),
                       "latency_median_s": statistics.median(lat), "latency_min_s": min(lat),
                       "latency_max_s": max(lat), "prompt_tokens_mean": statistics.mean(pt),
                       "prompt_tokens_max": max(pt),
                       "projected_hours_3000_calls": 3000 * statistics.mean(lat) / 3600},
        "raw_outputs": dict(Counter(x["raw_text"] for x in calls)),
        "finish_reasons": dict(Counter(x["finish_reason"] for x in calls)),
        "server_temperature_echo": dict(Counter(str(x["provider_meta"]["server_temperature_echo"]) for x in calls)),
        "harness": dict(Counter(x["harness"] for x in calls)),
    }


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("check", choices=["p4", "p5", "report"])
    ap.add_argument("--model", required=True, choices=[k for k, m in MODELS.items() if m["kind"] == "local"])
    a = ap.parse_args(argv)
    rep = {"check": a.check, "model": a.model, **{"p4": p4, "p5": p5, "report": report}[a.check](a.model)}
    write_json(CHECKS / f"{a.model}_{a.check}.json", rep)
    print(json.dumps(rep, indent=1, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
