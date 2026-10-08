"""Shared constants and helpers for experiment A1 (docs/experiment-protocol-a1.md).

Everything that the protocol fixes in advance lives here: paths, pinned hashes, seeds, the field order,
the information conditions, and how an alert's identity (content key, UID) is computed.
"""
from __future__ import annotations

import hashlib
import json
import os
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
TOOLS = ROOT / "tools"
CONFIG = ROOT / "config"
MANIFESTS = ROOT / "manifests"
RUNS = ROOT / "runs"
RESULTS = ROOT / "results"

DATASET = DATA / "secalertbench.json"
BENCH_SCRIPT = DATA / "run_rq1_api_test_eval.py"
PUBLISHED_DIR = DATA / "rq1"

# §0 pins (sha256). The Llama 3.2 3B GGUF hash is recorded by src/lock.py at first download.
PINS = {
    "secalertbench_commit": "42a84889fda912ca432c994924a1ccd4b9df6274",
    "secalertbench.json": "33f95305d1c42f8e615e4f94066119570859dee7eb086dff7c2273536c932ea3",
    "llama-b11509-bin-win-cuda-13.4-x64.zip": "12e4cf85d76aeef246cc793da9f2c62d03240505ce528bf180159665eaf66e2c",
    "cudart-llama-bin-win-cuda-13.4-x64.zip": "738f8c251ac22b70c3ae6f83a10cf222725df0395246a2cf58f32bdb85fbe668",
    "Qwen3-4B-Instruct-2507-Q4_K_M.gguf": "3605803b982cb64aead44f6c1b2ae36e3acdb41d8e46c8a94c6533bc4c67e597",
}

# §1 seeds
SEED_PRODUCTION = 20261009
SEED_DRYRUN = 20261010
SEED_CALL_ORDER = 20261011
SEED_BOOTSTRAP = 20261012
SEED_FOLDS = 20261009

DRYRUN_PER_STRATUM = 10
PRODUCTION_PER_STRATUM = 250
STRATA = ("mixed_attack", "single_attack", "mixed_non_attack", "single_non_attack")

# Context budget for local models: 8,192-token context minus 16 output tokens (§1, §3).
MAX_PROMPT_TOKENS = 8176

# §4.1: the dataset's own field order (identical in all 8,322 records; checked by load_dataset).
FIELD_ORDER = (
    "attack_type", "dip", "host", "method", "rule_name", "rsp_body", "kill_chain_all", "proto", "xff",
    "dport", "rsp_status", "parameter", "sip", "rsp_header", "uri", "req_header", "req_body", "sport",
)
CONDITIONS = {
    "a": (),
    "b": ("rule_name",),
    "c": ("rule_name", "attack_type", "kill_chain_all"),
}
IP_FIELDS = ("sip", "dip", "xff")
LABELS = ("Attack", "Non-Attack")


def sha256_bytes(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def sha256_text(s: str) -> str:
    return sha256_bytes(s.encode("utf-8"))


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def content_key(rec: dict) -> str:
    """Canonical JSON of every field except Label and the re-randomised IP fields (§1)."""
    return json.dumps({k: v for k, v in rec.items() if k != "Label" and k not in IP_FIELDS},
                      sort_keys=True, ensure_ascii=False)


def alert_uid(key: str) -> str:
    return sha256_text(key)[:16]


def load_dataset(check_hash: bool = True) -> list[dict]:
    if check_hash:
        got = sha256_file(DATASET)
        if got != PINS["secalertbench.json"]:
            raise SystemExit(f"secalertbench.json hash mismatch: {got}")
    data = json.load(open(DATASET, encoding="utf-8"))
    orders = {tuple(r.keys()) for r in data}
    if orders != {FIELD_ORDER + ("Label",)}:
        raise SystemExit(f"unexpected field order(s): {orders}")
    return data


def build_frame(data: list[dict]) -> tuple[list[dict], dict]:
    """Deduplicate by content key (lowest row index kept), drop label-conflicting keys, assign rule type.

    Returns (frame, info). Each frame row: row_index, uid, label, rule_name, rule_type, stratum.
    """
    labels_by_rule = defaultdict(set)
    for r in data:
        labels_by_rule[r["rule_name"]].add(r["Label"])
    rows_by_key: dict[str, list[int]] = {}
    for i, r in enumerate(data):
        rows_by_key.setdefault(content_key(r), []).append(i)
    frame, conflicting = [], []
    for key, idx in rows_by_key.items():
        labels = {data[i]["Label"] for i in idx}
        if len(labels) > 1:
            conflicting.append(alert_uid(key))
            continue
        i = min(idx)
        r = data[i]
        rule_type = "mixed" if len(labels_by_rule[r["rule_name"]]) == 2 else "single"
        lab = "attack" if r["Label"] == "Attack" else "non_attack"
        frame.append({
            "row_index": i, "uid": alert_uid(key), "label": r["Label"], "rule_name": r["rule_name"],
            "rule_type": rule_type, "stratum": f"{rule_type}_{lab}", "n_duplicates": len(idx),
        })
    if len({f["uid"] for f in frame}) != len(frame):
        raise SystemExit("UID collision in frame")
    frame.sort(key=lambda f: f["uid"])
    info = {"rows": len(data), "content_keys": len(rows_by_key), "conflicting_keys": conflicting,
            "frame": len(frame),
            "mixed_rules": sorted(r for r, s in labels_by_rule.items() if len(s) == 2)}
    return frame, info


def read_jsonl(path: Path) -> list[dict]:
    with open(path, encoding="utf-8") as f:
        return [json.loads(line) for line in f if line.strip()]


def write_jsonl(path: Path, rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        for r in rows:
            f.write(json.dumps(r, ensure_ascii=False, sort_keys=True) + "\n")


def write_json(path: Path, obj) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    with open(tmp, "w", encoding="utf-8", newline="\n") as f:
        json.dump(obj, f, ensure_ascii=False, indent=2, sort_keys=True)
        f.write("\n")
    os.replace(tmp, path)
