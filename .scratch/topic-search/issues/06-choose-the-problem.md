# Choose the problem

Type: grilling
Status: resolved
Blocked by: 01, 02, 03, 04, 05
Map: [Topic search](../map.md)

## Question

Given the four gap scans and the model setup, which candidate problem becomes the chosen problem, and which 1–2 become the rejected alternatives recorded in the brief? Compare the candidates against the rubric scores, the 7–10 day smallest-useful-version requirement, and the user's interests, then decide with the user.

## Answer

Decided with the user on 2026-10-08.

**Chosen problem: A, "Are LLM alert triagers better than cheap baselines?"** (from [Gap scan: LLM agents for SOC alert triage and log analysis](01-gap-scan-soc-alert-triage.md)). It has the strongest gap of the candidates (a flawed evaluation), the best feasibility and cost, needs no labelling, and is in cybersecurity. It isn't agentic (one LLM call per alert); that's accepted as AI-powered automation.

- **A1, core experiment:** a rule-shortcut audit on SecAlertBench. How much of the reported LLM performance comes from knowing which rule fired? Compare cheap non-LLM baselines on the mixed-label subset and under splits by unseen rule. The paper must stand on A1 alone if necessary.
- **A2, second experiment:** zero-shot LLMs vs risk-based alerting (RBA) on the public CATS datasets, as Uetz et al. (arXiv:2609.02465) ask. If time is tight, cut A2 to 2 CATS datasets rather than dropping it.

New fact found while deciding: the SecAlertBench repo (github.com/Dxsssu/SecAlertBench) publishes every model's prediction for every alert (`0x04. Evaluation Results/RQ1/`, 16 models). It also has an "Exp4" table of per-attack-type metrics for the top 5 attack types (`RQ2/Exp4/top5_attack_type_metrics.csv`), where LLM F1 on SQL injection is 0.09–0.50 even though TPR is 1.0. That table is a descriptive breakdown, not a baseline or shortcut audit, so the gap stands. A1 can reuse the published predictions instead of re-running the 16 models.

**Fallback problem: D**, LLMs vs KICS on docker-compose security misconfigurations, scored against hand-validated ground truth (from [Gap scan: LLM detection of Docker and infrastructure-as-code misconfigurations](04-gap-scan-docker-iac-misconfiguration.md)). D becomes the chosen problem if a kill criterion fires, without reopening the whole comparison.

**Kill criteria for A** (agreed thresholds; don't tighten or loosen them):

1. **Baseline:** with a saved script and the same cross-validation protocol, the rule-majority baseline does not reach the reported LLM average (F1 ≥ 0.71) on SecAlertBench.
2. **Data:** the published per-alert predictions can't be reliably matched to individual alerts, or the CATS datasets don't load with per-alert labels.
3. **Prior work:** a paper or preprint already reports a non-LLM baseline on SecAlertBench **and** one already compares LLMs with RBA on public alert data. If only one of them has been done, drop that part and keep the other rather than switching to D.
4. **Time:** in a 200-alert pilot, one local model's throughput projects to more than about 3 days of laptop compute for the planned runs, even after the A2 cut.

If none of these fires, proceed with A and don't reopen the topic comparison.

**Rejected candidate problems** (for the brief):

- **B, effect of n8n's built-in defences on prompt-injection rates** (from [Gap scan: Security of low-code AI workflow automation](02-gap-scan-low-code-workflow-security.md)): JAW (arXiv:2605.11229) already covers the core idea; what's left is a weak untested setting (gap 2, novelty 2), and providers' policies on adversarial testing are unchecked.
- **C, runtime reliability of LLM steps in public n8n templates** (from [Gap scan: Reliability of LLM agents in multi-step workflow automation](03-gap-scan-workflow-agent-reliability.md)): weak-to-moderate gap in a crowded area, and small local models are poor at multi-turn tool calling (see [Which LLMs can we actually run](05-feasible-model-setup.md)).

**How the kill criteria are checked:** [Feasibility pilot for SOC alert triage](08-feasibility-pilot-soc-alert-triage.md) covers criteria 1, 2 and 4, and [Prior-work check for SOC alert triage](09-prior-work-check-soc-alert-triage.md) covers criterion 3. Both block [Write and approve the problem brief](07-write-the-problem-brief.md).
