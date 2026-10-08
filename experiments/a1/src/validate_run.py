"""Validate one run directory after every session (protocol §9). Read-only: it never writes to the run.

  python -m src.validate_run --model llama-3.2-3b --subdir final [--phase dryrun] [--first N]

Checks: every line parses; no duplicate call_id; done IDs equal the expected IDs; every line's alert fields and
hashes match the manifest and the current harness; attempts show no completed call was re-sent.
"""
from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from pathlib import Path

from .common import MANIFESTS, RUNS, load_dataset, read_jsonl, sha256_file, sha256_text
from .prompts import SYSTEM_SHA256, user_message
from .run_llm import call_id, call_order, params_sha

PHASE_MANIFESTS = {"dryrun": MANIFESTS / "dryrun_sample.jsonl", "production": MANIFESTS / "shared_sample.jsonl"}


def _read_lines(path: Path) -> tuple[list[dict], list[int], bool]:
    """Parsed records, the 1-based numbers of unparseable lines, and whether the file ends in a partial line."""
    if not path.exists():
        return [], [], False
    raw = path.read_bytes()
    partial = bool(raw) and not raw.endswith(b"\n")
    recs, bad = [], []
    for n, line in enumerate(raw.decode("utf-8").splitlines(), 1):
        try:
            recs.append(json.loads(line))
        except json.JSONDecodeError:
            bad.append(n)
    return recs, bad, partial


def validate(run_dir: Path, phase: str, model_key: str, first: int | None = None, data=None) -> dict:
    manifest_path = PHASE_MANIFESTS[phase]
    manifest = read_jsonl(manifest_path)
    data = data if data is not None else load_dataset()
    psha = params_sha(model_key)
    order = call_order(manifest)[:first] if first else call_order(manifest)
    expected = {}
    for rec_m, cond in order:
        usha = sha256_text(user_message(data[rec_m["row_index"]], cond))
        expected[call_id(model_key, cond, rec_m["uid"], usha, psha)] = (rec_m, cond, usha)

    calls, bad_calls, partial = _read_lines(run_dir / "calls.jsonl")
    attempts, bad_attempts, partial_att = _read_lines(run_dir / "attempts.jsonl")
    meta_path = run_dir / "run_meta.json"
    meta = json.loads(meta_path.read_text(encoding="utf-8")) if meta_path.exists() else {}

    problems = []
    ids = [c["call_id"] for c in calls]
    dup = [k for k, n in Counter(ids).items() if n > 1]
    if dup:
        problems.append(f"{len(dup)} duplicate call_id(s)")
    if bad_calls or partial:
        problems.append(f"calls.jsonl: unparseable lines {bad_calls}, trailing partial line {partial}")
    if bad_attempts or partial_att:
        problems.append(f"attempts.jsonl: unparseable lines {bad_attempts}, trailing partial line {partial_att}")
    unexpected = [k for k in ids if k not in expected]
    if unexpected:
        problems.append(f"{len(unexpected)} call_id(s) not in the expected set")
    mism = Counter()
    for c in calls:
        if c["call_id"] not in expected:
            continue
        rec_m, cond, usha = expected[c["call_id"]]
        for field, want in (("alert_uid", rec_m["uid"]), ("row_index", rec_m["row_index"]),
                            ("stratum", rec_m["stratum"]), ("true_label", rec_m["label"]),
                            ("rule_name", rec_m["rule_name"]), ("condition", cond), ("user_sha256", usha),
                            ("system_sha256", SYSTEM_SHA256), ("params_sha256", psha), ("phase", phase),
                            ("model_key", model_key), ("config_hash", meta.get("config_hash"))):
            if c.get(field) != want:
                mism[field] += 1
    if mism:
        problems.append(f"fields not matching manifest/harness: {dict(mism)}")
    if meta and meta.get("manifest_sha256") != sha256_file(manifest_path):
        problems.append("run_meta manifest_sha256 differs from the manifest on disk")
    harnesses = Counter(c.get("harness") for c in calls)
    if len(harnesses) > 1:
        problems.append(f"calls from more than one harness: {dict(harnesses)}")

    done = set(ids)
    ok_attempts = Counter(a["call_id"] for a in attempts if a.get("status") == "ok")
    resent = sorted(k for k, n in ok_attempts.items() if n > 1)
    if resent:
        problems.append(f"{len(resent)} completed call(s) sent more than once")
    no_attempt = [k for k in done if ok_attempts[k] == 0]
    if no_attempt:
        problems.append(f"{len(no_attempt)} completed call(s) without an ok attempt")
    attempted = {a["call_id"] for a in attempts}
    failed = sorted(attempted - done)
    missing = sorted(set(expected) - done)

    status = Counter(c.get("status") for c in calls)
    complete = not missing
    return {
        "run_dir": str(run_dir), "phase": phase, "model": model_key, "pass": complete and not problems,
        "complete": complete, "expected": len(expected), "done": len(done), "missing": len(missing),
        "ok": status["ok"], "invalid": status["invalid"], "failed": len(failed),
        "attempts": len(attempts), "attempt_status": dict(Counter(a.get("status") for a in attempts)),
        "harness": dict(harnesses), "config_hash": meta.get("config_hash"), "sessions": len(meta.get("sessions", [])),
        "lock_present": (run_dir / "RUNNING.lock").exists(), "problems": problems,
    }


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--phase", default="dryrun", choices=sorted(PHASE_MANIFESTS))
    ap.add_argument("--model", required=True)
    ap.add_argument("--subdir", default="main")
    ap.add_argument("--first", type=int, default=None)
    a = ap.parse_args(argv)
    r = validate(RUNS / a.phase / a.model / a.subdir, a.phase, a.model, a.first)
    print(json.dumps(r, indent=1, ensure_ascii=False))
    return 0 if r["pass"] else 1


if __name__ == "__main__":
    sys.exit(main())
