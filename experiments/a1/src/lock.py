"""Protocol lock (protocol §0, §8): every pin and hash, seeds, model parameters and the harness identity.

  python -m src.lock                                   # write config/protocol.lock.json
  python -m src.lock --verify                          # recompute every recorded hash and compare
  python -m src.lock --label-tokens qwen3-4b           # record label tokens (llama-server running; tokenisation only)
  python -m src.lock --import-label-tokens llama-3.2-3b <run_meta.json>   # record tokens a runner already logged

The runner refuses to start unless the lock matches the files on disk and the current harness (run_llm.py).
Label tokens live in config/label_tokens.json (with their provenance) and are copied into the lock.
"""
from __future__ import annotations

import argparse
import importlib.metadata
import json
import platform
import subprocess
import sys

from .common import (BENCH_SCRIPT, CONDITIONS, CONFIG, DATASET, FIELD_ORDER, MANIFESTS, MAX_PROMPT_TOKENS, PINS,
                     PUBLISHED_DIR, ROOT, SEED_BOOTSTRAP, SEED_CALL_ORDER, SEED_DRYRUN, SEED_FOLDS,
                     SEED_PRODUCTION, TOOLS, sha256_file, sha256_text, write_json)
from .models import MODELS, model_params

LOCK_PATH = CONFIG / "protocol.lock.json"
LABEL_TOKENS_PATH = CONFIG / "label_tokens.json"
PACKAGES = ("numpy", "scikit-learn", "requests", "anthropic", "pytest")

# Settled decisions (protocol §12), as confirmed by the user. The protocol text itself is not edited.
DECISIONS = {
    "D1": "250 per stratum, uniform within strata, no per-rule cap, inverse-probability weights",
    "D2": "invalid responses never re-asked; counted as failures in primary metrics",
    "D3": "gpt-oss-120b: temperature 0, reasoning_effort low, max_completion_tokens 1024 (confirmed 2026-10-09)",
    "D4": "TF-IDF on visible alert fields only (§4.1), fitted per condition",
    "D5": "paired bootstrap; paired rule-cluster bootstrap as sensitivity analysis",
    "D6": "local models: llama-server /apply-template + /completion for probabilities (confirmed 2026-10-09)",
    "D7": "RQ1: all 2,000 published rows as published, labels from true_label (confirmed 2026-10-09)",
    "D8": "planned budget about $7-8 kept (confirmed 2026-10-09); API credentials not yet configured",
    "D9": "15 published per-alert files; gemini-3-flash-preview summary only",
    "D10": "RQ1 references: test input is each published row's own record; training on pinned-dataset rows outside "
           "the test set (exact content-key duplicates excluded); unmatched published rows kept, counted, reported "
           "as a limitation (protocol amendment 2026-10-09)",
}


def harness_hash() -> str:
    src = sorted((ROOT / "src").glob("*.py"))
    return sha256_text("".join(p.name + sha256_file(p) for p in src))[:16]


def _git(*args) -> str:
    return subprocess.run(["git", *args], cwd=ROOT, capture_output=True, text=True, check=True).stdout.strip()


def _rel(p) -> str:
    return p.relative_to(ROOT).as_posix()


def tracked_files() -> list:
    """Every input file the lock pins: dataset, benchmark script, published files, runtime, models, manifests."""
    files = [DATASET, BENCH_SCRIPT, *sorted(PUBLISHED_DIR.glob("*.json"))]
    files += [TOOLS / z for z in ("llama-b11509-bin-win-cuda-13.4-x64.zip", "cudart-llama-bin-win-cuda-13.4-x64.zip")]
    files += sorted((TOOLS / "llama.cpp").iterdir())
    files += [TOOLS / "models" / m["gguf"] for m in MODELS.values() if m["kind"] == "local"]
    files += sorted(MANIFESTS.glob("*.json*"))
    files += [ROOT / "requirements.txt", ROOT.parents[1] / "docs" / "experiment-protocol-a1.md",
              ROOT.parents[1] / "docs" / "problem-brief.md"]
    return [f for f in files if f.is_file()]


def build() -> dict:
    from .prompts import SYSTEM_SHA256, check_benchmark_sources
    files = {}
    for f in tracked_files():
        key = _rel(f) if f.is_relative_to(ROOT) else "../../" + f.relative_to(ROOT.parents[1]).as_posix()
        files[key] = sha256_file(f)
    pin_problems = [name for name, h in PINS.items() if name != "secalertbench_commit"
                    and not any(k.endswith("/" + name) and v == h for k, v in files.items())]
    if pin_problems:
        raise SystemExit(f"pinned hash mismatch or file missing: {pin_problems}")
    sources = check_benchmark_sources()
    if not all(sources.values()):
        raise SystemExit(f"benchmark sources differ from the pinned ones: {sources}")
    label_tokens = json.loads(LABEL_TOKENS_PATH.read_text(encoding="utf-8")) if LABEL_TOKENS_PATH.exists() else {}
    src_status = _git("status", "--porcelain", "--", "src")
    return {
        "protocol": "docs/experiment-protocol-a1.md (approved 2026-10-09; amended 2026-10-09: §4 test inputs, D10)",
        "pins": PINS, "files": files,
        "seeds": {"production": SEED_PRODUCTION, "dryrun": SEED_DRYRUN, "call_order": SEED_CALL_ORDER,
                  "bootstrap": SEED_BOOTSTRAP, "folds": SEED_FOLDS},
        "conditions": {k: list(v) for k, v in CONDITIONS.items()}, "field_order": list(FIELD_ORDER),
        "max_prompt_tokens": MAX_PROMPT_TOKENS,
        "models": {k: {"kind": m["kind"], "source": m.get("hf") or m.get("model_id"), "params": model_params(k)}
                   for k, m in MODELS.items()},
        "system_sha256": SYSTEM_SHA256, "benchmark_sources_identical": sources,
        "label_tokens": label_tokens,
        "decisions": DECISIONS,
        "environment": {"python": platform.python_version(),
                        "packages": {p: importlib.metadata.version(p) for p in PACKAGES}},
        "harness": {"hash": harness_hash(), "commit": _git("rev-parse", "HEAD"),
                    "src_uncommitted_changes": bool(src_status)},
    }


def load() -> dict:
    if not LOCK_PATH.exists():
        raise SystemExit(f"{LOCK_PATH} missing: run python -m src.lock")
    return json.loads(LOCK_PATH.read_text(encoding="utf-8"))


def verify(lock: dict, only=None) -> list[str]:
    """Problems found (empty = OK). `only` limits the file check to keys containing any of the given strings."""
    problems = []
    for key, want in lock["files"].items():
        if only is not None and not any(s in key for s in only):
            continue
        path = (ROOT / key).resolve()
        if not path.is_file():
            problems.append(f"missing: {key}")
        elif sha256_file(path) != want:
            problems.append(f"hash differs: {key}")
    if lock["harness"]["hash"] != harness_hash():
        problems.append(f"harness differs from the lock ({harness_hash()} vs {lock['harness']['hash']}): "
                        "regenerate the lock after any src/ change")
    for k in MODELS:
        if lock["models"][k]["params"] != model_params(k):
            problems.append(f"model parameters differ from the lock: {k}")
    return problems


def record_label_tokens(model_key: str, lt: dict, source: str) -> None:
    from datetime import datetime, timezone
    cur = json.loads(LABEL_TOKENS_PATH.read_text(encoding="utf-8")) if LABEL_TOKENS_PATH.exists() else {}
    cur[model_key] = {**lt, "source": source, "recorded_at": datetime.now(timezone.utc).isoformat(timespec="seconds")}
    write_json(LABEL_TOKENS_PATH, cur)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    g = ap.add_mutually_exclusive_group()
    g.add_argument("--verify", action="store_true")
    g.add_argument("--label-tokens", metavar="MODEL")
    g.add_argument("--import-label-tokens", nargs=2, metavar=("MODEL", "RUN_META"))
    a = ap.parse_args(argv)
    if a.verify:
        problems = verify(load())
        print(json.dumps({"pass": not problems, "problems": problems}, indent=1))
        return 0 if not problems else 1
    if a.label_tokens:
        from .models import LocalClient
        from .common import load_dataset, read_jsonl
        from .prompts import messages
        from .score import label_tokens
        m = MODELS[a.label_tokens]
        c = LocalClient()
        props = c.props()
        if not str(props.get("model_path")).endswith(m["gguf"]):
            raise SystemExit("server is not running this model")
        first = read_jsonl(MANIFESTS / "dryrun_sample.jsonl")[0]          # the runner's choice (run_llm.main)
        prompt = c.apply_template(messages(load_dataset()[first["row_index"]], "a"), m["template_kwargs"] or None)
        lt = label_tokens(c, prompt)
        record_label_tokens(a.label_tokens, lt, f"llama-server /tokenize, build {props.get('build_info')}")
        print(json.dumps(lt, ensure_ascii=False))
        return 0
    if a.import_label_tokens:
        model_key, path = a.import_label_tokens
        meta = json.loads(open(path, encoding="utf-8").read())
        if meta.get("model") != model_key:
            raise SystemExit(f"{path} is a run of {meta.get('model')}, not {model_key}")
        record_label_tokens(model_key, meta["label_tokens"],
                            f"logged by the runner in {path} (llama-server {meta['server']['build']}, "
                            f"{meta['params']['gguf']}); re-checked live by run_llm at every start")
        print(json.dumps(meta["label_tokens"], ensure_ascii=False))
        return 0
    lock = build()
    write_json(LOCK_PATH, lock)
    print(json.dumps({"lock": _rel(LOCK_PATH), "sha256": sha256_file(LOCK_PATH), "harness": lock["harness"],
                      "files": len(lock["files"]), "label_tokens": sorted(lock["label_tokens"])}, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())
