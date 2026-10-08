"""Summarise the (partial) Qwen3-4B throughput run and project compute for the planned local runs.
Run: python -X utf8 -P pilot/04_summarise_throughput.py -> results/04_throughput_summary.json
The run (03_*.py) was stopped by Claude Code's memory-pressure reaper after 118 of 200 alerts; this reads the JSONL it wrote.
"""
import json
import random
import statistics as st
from pathlib import Path

ROOT = Path(__file__).resolve().parent
rows = [json.loads(l) for l in open(ROOT / "results/03_throughput_qwen3_4b.jsonl", encoding="utf-8")]
ok = [r for r in rows if not r["error"]]
secs = [r["seconds"] for r in ok]
pt = [r["prompt_tokens"] for r in ok]
mean = st.mean(secs)
rng = random.Random(0)
boot = sorted(st.mean(rng.choices(secs, k=len(secs))) for _ in range(2000))
ci = (boot[50], boot[1949])
c = {k: sum(1 for r in ok if r["truth"] == t and r["pred"] == p) for k, (t, p) in
     {"TP": ("Attack", "Attack"), "FN": ("Attack", "Non-Attack"), "FP": ("Non-Attack", "Attack"), "TN": ("Non-Attack", "Non-Attack")}.items()}
# Planned local runs (see issue 06): A1 = mixed-label subset 3,471 + 1,000 single-label sample, per model, 2 local models;
# A2 reduced = 2 CATS datasets (170 + 172 alerts), 2 models; CATS prompts assumed no longer than SecAlertBench's.
plans = {
    "A1_two_models_4471_alerts_each": 2 * 4471,
    "A2_reduced_two_cats_sets_two_models": 2 * (170 + 172),
    "worst_case_A1_all_8322_alerts_two_models_plus_A2_reduced": 2 * 8322 + 2 * (170 + 172),
}
proj = {k: {"alerts": n, "hours_at_mean": n * mean / 3600, "hours_at_ci_high": n * ci[1] / 3600} for k, n in plans.items()}
out = {
    "alerts_completed": len(rows), "alerts_planned": 200, "request_errors": len(rows) - len(ok),
    "unparseable": sum(1 for r in ok if not r["pred"]),
    "seconds_per_alert": {"mean": mean, "mean_bootstrap_95ci": ci, "median": st.median(secs),
                          "p95": sorted(secs)[int(len(secs) * .95)], "max": max(secs)},
    "prompt_tokens": {"mean": st.mean(pt), "median": st.median(pt), "max": max(pt)},
    "confusion_zero_shot": c,
    "projection": proj, "kill_threshold_hours": 72,
    "criterion_4_fires": proj["worst_case_A1_all_8322_alerts_two_models_plus_A2_reduced"]["hours_at_ci_high"] > 72,
}
(ROOT / "results/04_throughput_summary.json").write_text(json.dumps(out, indent=2), encoding="utf-8")
print(json.dumps(out, indent=2))
