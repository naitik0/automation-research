"""Build the dry-run (40) and production shared (1,000) sample manifests (protocol §1) and the P14 report.

  python -m src.sample [--out-dir manifests]
Needs manifests/token_lengths_frame_<model>.jsonl for both local models (the §1 length check).
"""
from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path

import numpy as np

from .common import (DRYRUN_PER_STRATUM, MANIFESTS, MAX_PROMPT_TOKENS, PRODUCTION_PER_STRATUM, SEED_DRYRUN,
                     SEED_PRODUCTION, STRATA, build_frame, load_dataset, read_jsonl, sha256_file, write_json,
                     write_jsonl)
from .models import MODELS

LOCAL = [k for k, m in MODELS.items() if m["kind"] == "local"]


def draw(by_stratum: dict, n: int, seed: int) -> dict:
    g = np.random.Generator(np.random.PCG64(seed))
    out = {}
    for h in STRATA:
        pool = by_stratum[h]                      # sorted by UID
        idx = g.choice(len(pool), size=n, replace=False)
        out[h] = [pool[i] for i in sorted(idx)]
    return out


def concentration(rows: list[dict]) -> dict:
    rules = Counter(r["rule_name"] for r in rows)
    top_rule, top_n = rules.most_common(1)[0]
    per = {}
    for h in STRATA:
        c = Counter(r["rule_name"] for r in rows if r["stratum"] == h)
        name, n = c.most_common(1)[0]
        per[h] = {"alerts": sum(c.values()), "rules": len(c), "largest_rule_alerts": n,
                  "largest_rule_pct": round(100 * n / sum(c.values()), 1), "largest_rule": name}
    return {"alerts": len(rows), "unique_rules": len(rules), "largest_rule": top_rule, "largest_rule_alerts": top_n,
            "largest_rule_pct": round(100 * top_n / len(rows), 1), "per_stratum": per,
            "mixed_rules": len({r["rule_name"] for r in rows if r["stratum"].startswith("mixed")}),
            "single_rules": len({r["rule_name"] for r in rows if r["stratum"].startswith("single")})}


def build(out_dir: Path) -> dict:
    data = load_dataset()
    frame, info = build_frame(data)
    lengths = {}
    for m in LOCAL:
        for r in read_jsonl(MANIFESTS / f"token_lengths_frame_{m}.jsonl"):
            lengths.setdefault(r["uid"], {})[m] = r["tokens_a"]
    missing = [f["uid"] for f in frame if set(lengths.get(f["uid"], {})) != set(LOCAL)]
    if missing:
        raise SystemExit(f"{len(missing)} frame alerts lack token lengths for both local models")
    too_long = [f["uid"] for f in frame if max(lengths[f["uid"]].values()) > MAX_PROMPT_TOKENS]
    frame = [f for f in frame if f["uid"] not in set(too_long)]

    by_stratum = {h: [f for f in frame if f["stratum"] == h] for h in STRATA}
    n_frame = {h: len(v) for h, v in by_stratum.items()}
    dry = draw(by_stratum, DRYRUN_PER_STRATUM, SEED_DRYRUN)
    dry_uids = {r["uid"] for v in dry.values() for r in v}
    post = {h: [f for f in v if f["uid"] not in dry_uids] for h, v in by_stratum.items()}
    n_post = {h: len(v) for h, v in post.items()}
    prod = draw(post, PRODUCTION_PER_STRATUM, SEED_PRODUCTION)

    class_total = {"attack": n_post["mixed_attack"] + n_post["single_attack"],
                   "non_attack": n_post["mixed_non_attack"] + n_post["single_non_attack"]}
    weights = {h: 2 * n_post[h] / class_total["non_attack" if "non_attack" in h else "attack"] for h in STRATA}

    keep = ("uid", "row_index", "stratum", "label", "rule_name")
    dry_rows = [{**{k: r[k] for k in keep}, "weight": None} for h in STRATA for r in dry[h]]
    prod_rows = [{**{k: r[k] for k in keep}, "weight": weights[h]} for h in STRATA for r in prod[h]]
    write_jsonl(out_dir / "dryrun_sample.jsonl", dry_rows)
    write_jsonl(out_dir / "shared_sample.jsonl", prod_rows)
    summary = {
        "frame_info": {k: v for k, v in info.items() if k != "mixed_rules"},
        "mixed_rules_total": len(info["mixed_rules"]),
        "excluded_too_long": len(too_long), "frame_per_stratum": n_frame,
        "post_dryrun_per_stratum": n_post, "post_dryrun_total": sum(n_post.values()),
        "weights": weights, "class_post_dryrun_totals": class_total,
        "dryrun_sha256": sha256_file(out_dir / "dryrun_sample.jsonl"),
        "shared_sha256": sha256_file(out_dir / "shared_sample.jsonl"),
        "overlap_dryrun_production": len(dry_uids & {r["uid"] for r in prod_rows}),
        "p14_concentration_shared_sample": concentration(prod_rows),
    }
    write_json(out_dir / "sample_summary.json", summary)
    return summary


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--out-dir", default=str(MANIFESTS))
    s = build(Path(ap.parse_args().out_dir))
    print(json.dumps({k: s[k] for k in ("excluded_too_long", "post_dryrun_total", "weights", "dryrun_sha256",
                                        "shared_sha256")}, indent=1))
