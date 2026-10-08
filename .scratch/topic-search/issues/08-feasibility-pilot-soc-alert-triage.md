# Feasibility pilot for SOC alert triage

Type: task
Status: resolved
Blocked by: 06
Map: [Topic search](../map.md)
Findings: [notes/soc-alert-triage-pilot.md](../../../notes/soc-alert-triage-pilot.md); scripts, pinned versions and raw results in [pilot/](../../../pilot/README.md)

## Question

Do kill criteria 1, 2 and 4 from [Choose the problem](06-choose-the-problem.md) fire for the chosen problem? AFK, time-boxed to about 3 hours. This is a smoke test, not the experiment.

1. **Baseline (criterion 1):** download `secalertbench.json` from github.com/Dxsssu/SecAlertBench and re-run the rule-majority baseline (predict each `rule_name`'s majority label, learned on the training folds; 5-fold random cross-validation, 3 seeds) with a **saved script**. Report F1, TPR and FPR against the reported LLM average (F1 0.7092, FPR 0.4413). The criterion fires if F1 < 0.71.
2. **Data (criterion 2):**
   - Check that the per-model prediction files in `0x04. Evaluation Results/RQ1/` match individual alerts in the dataset one-to-one: shared IDs or an exact record match, and the counts agree.
   - Recompute one model's reported F1 from its file.
   - Count the mixed-label subset (rules that carry both labels).
   - Load 2 small CATS datasets (github.com/962012d09b/cats, `/datasets`, e.g. the two SOCBED sets) and confirm they have per-alert labels.
3. **Throughput (criterion 4):** run Qwen3-4B-Instruct-2507 (Q4_K_M, Ollama) zero-shot on 200 SecAlertBench alerts, measuring seconds per alert and the parse-failure rate. Project the time for the planned local runs: the A1 audit runs plus A2 on the CATS datasets, and the reduced A2 (2 datasets). Criterion 4 fires if even the reduced plan projects to more than about 3 days of laptop compute.

Save scripts under `pilot/` and record the results (numbers, commands, a verdict on each criterion) in `notes/soc-alert-triage-pilot.md`. If a criterion fires, say which one and stop; switching to the fallback problem is decided on the map, not here.

## Answer

**Verdict: none of kill criteria 1, 2 and 4 fired.** A stays the chosen problem. Pilot ran 2026-10-08, about 2h15m of the 3-hour box.

1. **Baseline (criterion 1): does not fire.** Scored per model on each model's own balanced 2,000-alert sample (the LLMs were not run on all 8,322 alerts, and each model got a different random sample), a rule-majority lookup reaches F1 **0.898** (95% CI 0.894–0.901), TPR 0.844, FPR 0.036, against the LLM average of F1 0.709, TPR 0.797, FPR 0.441. The LLM average recomputed from the released files equals the paper's headline numbers exactly. On the mixed-label slice the baseline still wins (F1 0.763 vs 0.578). The earlier gap-scan figure of F1 0.89 was on the natural 30%-Attack distribution; quote 0.898.
2. **Data (criterion 2): does not fire.** Released predictions have no alert IDs and were made on records with different IP addresses, but match the dataset by content for 99.8% of rows with no rule conflicts, and each prediction row carries its own record and label anyway. Both small CATS datasets (SOCBED Suricata 170 alerts, SOCBED Sigma 172) load with per-alert labels. **One of the 16 prediction files (Gemini) is removed by Windows Defender**, so 15 were analysed; its summary was read from the file header.
3. **Time (criterion 4): does not fire.** Qwen3-4B-Instruct-2507 Q4_K_M on the GTX 1650 took 9.0 s/alert on average (CI 7.8–10.2). The planned local runs project to about 24–27 h; the worst case (all 8,322 alerts, two models) to about 49 h, against the 72 h threshold. **Caveat: the run covered 118 of 200 alerts** — Claude Code stopped it when the machine ran out of RAM, and it was not restarted. llama.cpp (portable build) was used instead of Ollama.

**Findings for the brief:** zero-shot Qwen3-4B answered "Attack" for all 118 alerts (FPR 1.0), so report TPR/FPR or AUROC, not F1 alone; the LLMs also see `rule_name`, so a hidden-rule arm is needed to separate the two; rule lookup cannot generalise to unseen rules (grouped splits need a content-based baseline); and the baseline is supervised while the LLMs are zero-shot. Details in the note.
