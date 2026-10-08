# Gap scan: LLM agents for SOC alert triage and log analysis

Type: research
Status: resolved
Blocked by: none
Map: [Topic search](../map.md)
Findings: [notes/soc-alert-triage-gap-scan.md](../../../notes/soc-alert-triage-gap-scan.md) (also on branch `research/soc-alert-triage`)

## Question

Where is the strongest research gap in using LLMs or LLM agents to triage security alerts or analyse security logs (e.g. classifying alerts as true/false positives, explaining log events, mapping to MITRE ATT&CK), and is it feasible for us? Answer using the gap-scan rubric in the map's Notes. Pay particular attention to how crowded this area is in 2025–2026 and which public alert/log datasets have ground-truth labels.

## Answer

**Verdict: the area is crowded, but it has the strongest gap of the four (a flawed evaluation).** There are 15+ papers and benchmarks from 2025–2026, most from April–September 2026, covering agentic investigation, SOC benchmarks, prompt injection through logs, and log-to-ATT&CK mapping. Those sub-areas are rejected.

**The gap:** published LLM alert-triage results don't compare against cheap non-LLM baselines, and the labels may be largely predictable from which rule fired. In a pilot on public SecAlertBench (8,322 alerts), a lookup baseline predicting each rule's majority label (5-fold cross-validation, 3 seeds) scored F1 0.89 and a false-positive rate of 0.04. The 16 LLMs reported for the benchmark averaged F1 0.71 and a false-positive rate of 0.44. 210 of 241 rules only ever carry one label. The comparison isn't like-for-like: the baseline learns from labels, while the LLMs are zero-shot. Uetz et al. (arXiv:2609.02465, listed as USENIX Security '27) explicitly call for LLM triage to be compared against risk-based alerting (RBA), and no paper has done so yet.

Recommended candidate problem (candidates 1 and 2 merged): *Are LLM alert triagers better than cheap baselines?* That means measuring how much of LLM triage performance comes from knowing which rule fired (the mixed-label subset, and splits by unseen rule), and whether zero-shot LLMs beat RBA on the seven public CATS datasets (AUROC, false-positive burden at fixed recall, token cost). A weaker add-on: does giving the LLM same-host alert context close the gap?

Scores: gap 4, novelty 3, feasibility 5, data 4, cost 5, speed 4.

**Conditions before choosing this:**
- The pilot script wasn't saved. Reproduce the baseline as the first step of any feasibility pilot.
- The SecAlertBench paper itself wasn't found or read, and it may already break results down by rule. Find and read it.
- Re-check the Uetz et al. venue claim.
- Neither SecAlertBench nor CATS has a licence file, so research use with citation only; ask the authors before redistributing data.
- SecAlertBench rule names and attack types are in Chinese. Use multilingual models (Qwen), or translate them.
- Risk of being beaten to it: "LLM vs RBA" is an obvious next paper after Uetz et al.
