"""Prompt token lengths under each local model's chat template (protocol §1 length check, P3).

  python -m src.token_lengths --model qwen3-4b --scope frame    # condition (a), all frame alerts (before sampling)
  python -m src.token_lengths --model qwen3-4b --scope samples  # conditions a/b/c, dry-run + production samples
The matching llama-server must be running.
"""
from __future__ import annotations

import argparse
import json

from .common import MANIFESTS, build_frame, load_dataset, read_jsonl, write_jsonl
from .models import MODELS, LocalClient
from .prompts import messages


def main(argv=None) -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", required=True, choices=[k for k, m in MODELS.items() if m["kind"] == "local"])
    ap.add_argument("--scope", required=True, choices=["frame", "samples"])
    a = ap.parse_args(argv)
    c = LocalClient()
    if not str(c.props().get("model_path")).endswith(MODELS[a.model]["gguf"]):
        raise SystemExit("server is not running this model")
    kw = MODELS[a.model]["template_kwargs"] or None
    data = load_dataset()
    if a.scope == "frame":
        rows, conds = build_frame(data)[0], ("a",)
    else:
        rows = read_jsonl(MANIFESTS / "dryrun_sample.jsonl") + read_jsonl(MANIFESTS / "shared_sample.jsonl")
        conds = ("a", "b", "c")
    out = []
    for r in rows:
        rec = data[r["row_index"]]
        out.append({"uid": r["uid"], **{f"tokens_{cond}": len(c.tokenize(c.apply_template(messages(rec, cond), kw)))
                                        for cond in conds}})
    path = MANIFESTS / f"token_lengths_{a.scope}_{a.model}.jsonl"
    write_jsonl(path, out)
    mx = {cond: max(o[f"tokens_{cond}"] for o in out) for cond in conds}
    print(json.dumps({"model": a.model, "scope": a.scope, "alerts": len(out), "max_tokens": mx}))


if __name__ == "__main__":
    main()
