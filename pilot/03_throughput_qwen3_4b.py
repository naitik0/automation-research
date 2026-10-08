"""Pilot criterion 4: zero-shot Qwen3-4B-Instruct-2507 (Q4_K_M, llama.cpp) on 200 SecAlertBench alerts.

Uses SecAlertBench's own system prompt, user-content format and parsing (scripts/run_rq1_api_test_eval.py, pinned
commit 42a8488), temperature 0, so latency reflects real prompt lengths. Sequential requests (true per-alert latency).
Sample: 100 Attack + 100 Non-Attack, random.Random(42), from secalertbench_attack/non-attack split of the full file.
Run (server on :8089):  python -X utf8 -P pilot/03_throughput_qwen3_4b.py  -> results/03_throughput_qwen3_4b.json(l)
"""
import json
import random
import time
from pathlib import Path

import requests

ROOT = Path(__file__).resolve().parent
URL = "http://127.0.0.1:8089/v1/chat/completions"
N_PER_CLASS = 100
SYSTEM_PROMPT = """
<task description>
You will be given one network alert record and your task is to classify the alert into one of two labels:
- Attack: The alert indicates a real malicious activity, an attack attempt, or other security-threatening actions.
- Non-Attack: The alert does not indicate a real attack. It may correspond to benign traffic, normal operations, false positives, or informational events.
<constraints>
Do not output explanations or any additional text. Return only "Attack" or "Non-Attack".
"""


def build_user_content(record):
    return "Alert fields (JSON):\n" + json.dumps(dict(record), ensure_ascii=False, indent=2)


def parse_label(content):
    text = str(content).strip()
    if text in ("Attack", "Non-Attack"):
        return text
    if "Non-Attack" in text:
        return "Non-Attack"
    if "Attack" in text:
        return "Attack"
    return None


def main():
    data = json.load(open(ROOT / "data/secalertbench/secalertbench.json", encoding="utf-8"))
    rng = random.Random(42)
    att = [r for r in data if r["Label"] == "Attack"]
    non = [r for r in data if r["Label"] == "Non-Attack"]
    tasks = [(r, "Attack") for r in rng.sample(att, N_PER_CLASS)] + [(r, "Non-Attack") for r in rng.sample(non, N_PER_CLASS)]
    rng.shuffle(tasks)
    props = requests.get("http://127.0.0.1:8089/props", timeout=10).json()
    rows, t_all = [], time.time()
    out_jsonl = open(ROOT / "results/03_throughput_qwen3_4b.jsonl", "w", encoding="utf-8")
    for i, (rec, truth) in enumerate(tasks):
        body = {"messages": [{"role": "system", "content": SYSTEM_PROMPT},
                             {"role": "user", "content": build_user_content({k: v for k, v in rec.items() if k != "Label"})}],
                "temperature": 0, "max_tokens": 8, "stream": False}
        t0 = time.time()
        err = None
        try:
            resp = requests.post(URL, json=body, timeout=300)
            j = resp.json()
            if not resp.ok:
                err = str(j)[:200]
            else:
                raw = j["choices"][0]["message"]["content"]
                usage = j.get("usage", {})
        except Exception as e:  # noqa: BLE001
            err = repr(e)[:200]
        dt = time.time() - t0
        row = {"i": i, "truth": truth, "rule_name": rec["rule_name"], "seconds": dt, "error": err}
        if not err:
            row.update({"raw": raw, "pred": parse_label(raw), "prompt_tokens": usage.get("prompt_tokens"),
                        "completion_tokens": usage.get("completion_tokens")})
        rows.append(row)
        out_jsonl.write(json.dumps(row, ensure_ascii=False) + "\n")
        if i % 25 == 0:
            print(i, f"{dt:.2f}s", row.get("pred"), row.get("prompt_tokens"), err, flush=True)
    total = time.time() - t_all
    ok = [r for r in rows if not r["error"]]
    valid = [r for r in ok if r["pred"]]
    tp = sum(r["truth"] == "Attack" and r["pred"] == "Attack" for r in valid)
    fp = sum(r["truth"] == "Non-Attack" and r["pred"] == "Attack" for r in valid)
    fn = sum(r["truth"] == "Attack" and r["pred"] == "Non-Attack" for r in valid)
    tn = sum(r["truth"] == "Non-Attack" and r["pred"] == "Non-Attack" for r in valid)
    prec = tp / (tp + fp) if tp + fp else 0
    tpr = tp / (tp + fn) if tp + fn else 0
    secs = sorted(r["seconds"] for r in ok)
    pt = sorted(r["prompt_tokens"] for r in ok if r.get("prompt_tokens"))
    summary = {
        "model": "Qwen3-4B-Instruct-2507-Q4_K_M.gguf", "server_props_build": props.get("build_info"),
        "n": len(rows), "request_errors": len(rows) - len(ok), "unparseable": len(ok) - len(valid),
        "total_wall_s": total, "mean_s_per_alert": sum(secs) / len(secs), "median_s": secs[len(secs) // 2],
        "p95_s": secs[int(len(secs) * .95)], "max_s": secs[-1],
        "prompt_tokens_median": pt[len(pt) // 2], "prompt_tokens_p95": pt[int(len(pt) * .95)], "prompt_tokens_max": pt[-1],
        "confusion": {"TP": tp, "FP": fp, "TN": tn, "FN": fn},
        "tpr": tpr, "fpr": fp / (fp + tn) if fp + tn else 0, "precision": prec,
        "f1": 2 * prec * tpr / (prec + tpr) if prec + tpr else 0,
    }
    (ROOT / "results/03_throughput_qwen3_4b.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
