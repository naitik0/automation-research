"""Pilot criterion 2 (CATS): do two small CATS datasets load with per-alert labels?
Run: python -X utf8 -P pilot/02_cats_load.py   -> pilot/results/02_cats_load.json
"""
import json
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent
out = {}
for name in ("socbed_suricata", "socbed_sigma"):
    rows = [json.loads(l) for l in open(ROOT / "data/cats" / name / f"{name}.jsonl", encoding="utf-8") if l.strip()]
    keys = Counter(k for r in rows for k in r)
    lab = Counter(bool(r["full_alert"]["metadata"]["misuse"]) for r in rows)
    rules = Counter(r["features"]["rule_name"] for r in rows)
    out[name] = {"n": len(rows), "label_misuse_counts": {str(k): v for k, v in lab.items()}, "distinct_rules": len(rules), "top_level_keys": dict(keys.most_common(30)), "first_row": rows[0]}
    print(name, len(rows), "labels(misuse):", dict(lab), "distinct rules:", len(rules))
(ROOT / "results/02_cats_load.json").write_text(json.dumps(out, indent=2, ensure_ascii=False)[:200000], encoding="utf-8")
