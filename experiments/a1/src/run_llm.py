"""Checkpointed, resumable LLM runner (protocol §3, §8, §9). Dry run only: production is disabled in code.

  python -m src.run_llm --model qwen3-4b [--max-new-calls 60] [--subdir main] [--first N]
  python -m src.run_llm --model llama-3.2-3b --print-config   # offline: config and hashes, no server or API
  test hooks (P10): --crash-after N [--crash-partial]

Before any request the runner checks config/protocol.lock.json against the files on disk and the current
harness, and checks the live label tokens against the lock. A run directory written by another harness is
never resumed: use a new --subdir.
"""
from __future__ import annotations

import argparse
import json
import os
import random
import socket
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

import numpy as np

from .common import MANIFESTS, RUNS, SEED_CALL_ORDER, load_dataset, read_jsonl, sha256_file, sha256_text, write_json
from .lock import LOCK_PATH, harness_hash
from .lock import load as load_lock
from .lock import verify as verify_lock
from .models import (MODELS, AnthropicClient, FatalError, GroqClient, LocalClient, TransportError,
                     model_params)
from .prompts import SYSTEM_PROMPT, SYSTEM_SHA256, messages, parse_label, user_message
from .score import extract_score, label_tokens

ALLOWED_PHASES = {"dryrun": MANIFESTS / "dryrun_sample.jsonl"}  # production deliberately absent (§11)
BACKOFF = (2, 4, 8, 16, 32, 60)
MAX_ATTEMPTS = 6
LABEL_TOKEN_KEYS = ("A", "A_pieces", "N", "N_pieces", "k", "prompt_prefix_unchanged")


def now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="milliseconds")


def call_order(manifest: list[dict]) -> list[tuple[dict, str]]:
    uids = sorted(r["uid"] for r in manifest)
    by_uid = {r["uid"]: r for r in manifest}
    perm = np.random.Generator(np.random.PCG64(SEED_CALL_ORDER)).permutation(len(uids))
    return [(by_uid[uids[i]], c) for i in perm for c in ("a", "b", "c")]


def params_sha(model_key: str) -> str:
    return sha256_text(json.dumps(model_params(model_key), sort_keys=True))


def call_id(model_key, cond, uid, user_sha, psha) -> str:
    return sha256_text(f"{model_key}|{cond}|{uid}|{SYSTEM_SHA256}|{user_sha}|{psha}")


class Store:
    """Append-only calls.jsonl + attempts.jsonl with fsync, partial-line recovery and a run lock."""

    def __init__(self, run_dir: Path, config_hash: str, meta: dict, break_lock: bool):
        self.dir = run_dir
        self.calls, self.attempts = run_dir / "calls.jsonl", run_dir / "attempts.jsonl"
        self.lock = run_dir / "RUNNING.lock"
        meta_path = run_dir / "run_meta.json"
        old = json.loads(meta_path.read_text(encoding="utf-8")) if meta_path.exists() else None
        # Every refusal comes before the first write, so a refused start leaves the run directory untouched.
        if self.lock.exists() and not break_lock:
            raise SystemExit(f"{self.lock} exists (another runner, or a stale lock: use --break-lock)")
        if old is not None:
            if old["config_hash"] != config_hash:
                raise SystemExit("config hash differs from run_meta.json: refusing to resume (§9)")
            harnesses = {s.get("harness") for s in old.get("sessions", [])}
            if harnesses != {meta["harness"]}:
                raise SystemExit(f"{run_dir} was written by harness {sorted(map(str, harnesses))}, not "
                                 f"{meta['harness']}: refusing to mix harnesses in one run (use a new --subdir)")
        run_dir.mkdir(parents=True, exist_ok=True)
        self.lock.write_text(json.dumps({"pid": os.getpid(), "host": socket.gethostname(), "since": now()}))
        if old is not None:
            old["sessions"].append({"started": now(), "harness": meta["harness"]})
            write_json(meta_path, old)
        else:
            write_json(meta_path, {**meta, "config_hash": config_hash,
                                   "sessions": [{"started": now(), "harness": meta["harness"]}]})
        try:
            self.done = self._load()
        except SystemExit:
            self.release()
            raise

    def _load(self) -> dict:
        if not self.calls.exists():
            return {}
        raw = self.calls.read_bytes()
        if raw and not raw.endswith(b"\n"):
            cut = raw.rfind(b"\n") + 1
            (self.dir / f"calls.jsonl.partial-{int(time.time())}").write_bytes(raw[cut:])
            with open(self.calls, "r+b") as f:
                f.truncate(cut)
            print(f"recovered: moved a {len(raw) - cut}-byte partial line aside", file=sys.stderr)
        done = {}
        for line in self.calls.read_text(encoding="utf-8").splitlines():
            rec = json.loads(line)
            if rec["call_id"] in done:
                raise SystemExit(f"duplicate call_id {rec['call_id']} in calls.jsonl")
            done[rec["call_id"]] = rec
        return done

    @staticmethod
    def _append(path: Path, obj: dict, partial: bool = False) -> None:
        line = json.dumps(obj, ensure_ascii=False, sort_keys=True) + "\n"
        with open(path, "a", encoding="utf-8", newline="\n") as f:
            f.write(line[: len(line) // 2] if partial else line)
            f.flush()
            os.fsync(f.fileno())

    def record_attempt(self, obj: dict) -> None:
        self._append(self.attempts, obj)

    def record_call(self, obj: dict, partial: bool = False) -> None:
        self._append(self.calls, obj, partial)
        if not partial:
            self.done[obj["call_id"]] = obj

    def release(self) -> None:
        if self.lock.exists():
            self.lock.unlink()


def do_call(model_key: str, client, rec: dict, cond: str, lt: dict | None, params: dict) -> dict:
    """One request. Returns the fields of the calls.jsonl line that depend on the provider."""
    kind = MODELS[model_key]["kind"]
    msgs = messages(rec, cond)
    t0 = time.time()
    if kind == "local":
        prompt = client.apply_template(msgs, params["template_kwargs"] or None)
        r = client.completion(prompt)
        cp = r["completion_probabilities"]
        k = lt["k"]
        out = {
            "raw_text": r["content"], "finish_reason": r.get("stop_type"),
            "usage": {"prompt_tokens": r.get("tokens_evaluated"), "completion_tokens": r.get("tokens_predicted")},
            "generated_token_ids": [p["id"] for p in cp],
            "top_logprobs_to_k": [[[t["id"], t["token"], t["logprob"]] for t in p["top_logprobs"]] for p in cp[:k]],
            "rendered_prompt_sha256": sha256_text(prompt),
            "provider_meta": {"server_temperature_echo": r.get("generation_settings", {}).get("temperature")},
        }
        sc = extract_score(cp, lt)
        out.update({"score_available": sc["available"], "score_attack": sc.get("s"),
                    "p_A": sc.get("p_A"), "p_N": sc.get("p_N"), "score_unavailable_reason": sc.get("reason")})
    elif kind == "groq":
        j, meta = client.chat(msgs, params)
        ch = j["choices"][0]
        out = {"raw_text": ch["message"].get("content"), "finish_reason": ch.get("finish_reason"),
               "reasoning_text": ch["message"].get("reasoning"), "usage": j.get("usage"),
               "provider_meta": {"system_fingerprint": j.get("system_fingerprint"), "response_model": j.get("model"),
                                 "response_id": j.get("id"), **meta}}
    else:
        m = client.create(SYSTEM_PROMPT, user_message(rec, cond), params)
        text = "".join(b.text for b in m.content if getattr(b, "type", None) == "text")
        out = {"raw_text": text, "finish_reason": m.stop_reason,
               "usage": {"prompt_tokens": m.usage.input_tokens, "completion_tokens": m.usage.output_tokens},
               "provider_meta": {"response_model": m.model, "response_id": m.id}}
    out["latency_s"] = time.time() - t0
    return out


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--phase", default="dryrun")
    ap.add_argument("--model", required=True, choices=sorted(MODELS))
    ap.add_argument("--subdir", default="main")
    ap.add_argument("--first", type=int, default=None, help="only the first N calls in call order")
    ap.add_argument("--max-new-calls", type=int, default=None)
    ap.add_argument("--break-lock", action="store_true")
    ap.add_argument("--crash-after", type=int, default=None, help="P10 test hook: hard exit after N new calls")
    ap.add_argument("--crash-partial", action="store_true", help="P10: write half of the next line before exiting")
    ap.add_argument("--print-config", action="store_true", help="print config and hashes offline, then exit")
    a = ap.parse_args(argv)

    if a.phase not in ALLOWED_PHASES:
        raise SystemExit("Production runs are disabled until the dry-run report is approved (protocol §11).")
    manifest_path = ALLOWED_PHASES[a.phase]
    params = model_params(a.model)
    psha = params_sha(a.model)
    kind = MODELS[a.model]["kind"]

    # §0: refuse to start unless the pinned inputs and the harness match the lock.
    lock = load_lock()
    only = ["data/secalertbench.json", "data/run_rq1_api_test_eval.py", "manifests/" + manifest_path.name]
    if kind == "local":
        only += ["tools/models/" + MODELS[a.model]["gguf"], "tools/llama.cpp/llama", "tools/llama.cpp/ggml"]
    problems = verify_lock(lock, only)
    if problems:
        raise SystemExit("protocol lock check failed: " + "; ".join(problems))
    lt = None
    if kind == "local":
        if a.model not in lock["label_tokens"]:
            raise SystemExit(f"no label tokens for {a.model} in the lock (python -m src.lock --label-tokens)")
        lt = {k: lock["label_tokens"][a.model][k] for k in LABEL_TOKEN_KEYS}

    order = call_order(read_jsonl(manifest_path))
    if a.first:
        order = order[: a.first]
    config = {"phase": a.phase, "model": a.model, "params": params, "manifest_sha256": sha256_file(manifest_path),
              "system_sha256": SYSTEM_SHA256, "label_tokens": lt, "first": a.first}
    config_hash = sha256_text(json.dumps(config, sort_keys=True))
    meta = {**config, "harness": harness_hash(), "host": socket.gethostname(),
            "lock_sha256": sha256_file(LOCK_PATH), "harness_commit_in_lock": lock["harness"]["commit"]}
    if a.print_config:
        print(json.dumps({"config_hash": config_hash, "harness": meta["harness"], "lock_sha256": meta["lock_sha256"],
                          "expected_calls": len(order), "run_dir": str(RUNS / a.phase / a.model / a.subdir),
                          "config": config}, indent=1, ensure_ascii=False))
        return 0

    manifest = read_jsonl(manifest_path)
    data = load_dataset()
    client = {"local": LocalClient, "groq": GroqClient, "anthropic": AnthropicClient}[kind]()
    server = None
    if kind == "local":
        props = client.props()
        server = {"build": props.get("build_info"), "model_path": props.get("model_path")}
        if not str(server["model_path"]).endswith(MODELS[a.model]["gguf"]):
            raise SystemExit(f"server is running {server['model_path']}, not {a.model}")
        first_rec = data[manifest[0]["row_index"]]
        live = label_tokens(client, client.apply_template(messages(first_rec, "a"), params["template_kwargs"] or None))
        if live != lt:                                 # §7.1 step 2 / P8: the tokens must be the recorded ones
            raise SystemExit(f"live label tokens differ from the lock: {live} vs {lt}")
    meta["server"] = server
    store = Store(RUNS / a.phase / a.model / a.subdir, config_hash, meta, a.break_lock)

    new = 0
    try:
        for rec_m, cond in order:
            rec = data[rec_m["row_index"]]
            usha = sha256_text(user_message(rec, cond))
            cid = call_id(a.model, cond, rec_m["uid"], usha, psha)
            if cid in store.done:
                continue
            if a.max_new_calls is not None and new >= a.max_new_calls:
                break
            result = None
            for attempt in range(1, MAX_ATTEMPTS + 1):
                started = now()
                try:
                    result = do_call(a.model, client, rec, cond, lt, params)
                    store.record_attempt({"call_id": cid, "attempt": attempt, "started": started, "status": "ok",
                                          "latency_s": result["latency_s"]})
                    break
                except TransportError as e:
                    store.record_attempt({"call_id": cid, "attempt": attempt, "started": started, "status": "error",
                                          "http_status": e.status, "error": str(e)[:300]})
                    if attempt < MAX_ATTEMPTS:
                        delay = BACKOFF[attempt - 1] * random.uniform(0.9, 1.1)
                        time.sleep(max(delay, e.retry_after or 0))
                except FatalError as e:
                    store.record_attempt({"call_id": cid, "attempt": attempt, "started": started, "status": "fatal",
                                          "error": str(e)[:300]})
                    raise SystemExit(f"fatal (non-retryable) error, run stopped: {e}")
            if result is None:  # failed: not done, retried on the next resume (§3)
                continue
            parsed = parse_label(result["raw_text"])
            line = {
                "call_id": cid, "phase": a.phase, "model_key": a.model,
                "model_id": params.get("model_id", MODELS[a.model].get("gguf")), "condition": cond,
                "alert_uid": rec_m["uid"], "row_index": rec_m["row_index"], "stratum": rec_m["stratum"],
                "true_label": rec_m["label"], "rule_name": rec_m["rule_name"],
                "system_sha256": SYSTEM_SHA256, "user_sha256": usha, "params_sha256": psha,
                "status": "ok" if parsed else "invalid", "parsed_label": parsed,
                "n_attempts": attempt, "completed_at": now(), "harness": meta["harness"], "config_hash": config_hash,
                **result,
            }
            crash_now = a.crash_after is not None and new + 1 >= a.crash_after
            if crash_now and a.crash_partial:
                store.record_call(line, partial=True)
                os._exit(3)
            store.record_call(line)
            new += 1
            if crash_now:
                os._exit(3)
    finally:
        store.release()
    n_ok = sum(1 for r in store.done.values() if r["status"] == "ok")
    print(json.dumps({"model": a.model, "subdir": a.subdir, "new_calls": new, "done": len(store.done),
                      "expected": len(order), "ok": n_ok, "invalid": len(store.done) - n_ok}))
    return 0


if __name__ == "__main__":
    sys.exit(main())
