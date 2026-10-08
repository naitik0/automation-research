# Prior-work check for SOC alert triage

Type: research
Status: resolved
Blocked by: 06
Map: [Topic search](../map.md)
Findings: [notes/soc-alert-triage-prior-work.md](../../../notes/soc-alert-triage-prior-work.md) (also on branch `research/soc-alert-triage-prior-work`)

## Question

Does kill criterion 3 from [Choose the problem](06-choose-the-problem.md) fire? Has any paper or preprint (up to October 2026) (a) reported a non-LLM baseline (rule lookup, majority, ML) on SecAlertBench, or audited how much its labels can be predicted from the rule name; or (b) compared LLM alert triage with risk-based alerting (RBA) on public alert data such as the CATS datasets? Report (a) and (b) separately. If only one has been done, that part is dropped and the other kept; if both have been done, the criterion fires.

Also:
- Find the SecAlertBench paper ("SecAlertBench: Evaluating Large Language Models for Tier-1 Alert Triage in Security Operations Centers"): arXiv ID or venue, authors, and whether it discusses baselines or rule-level shortcuts beyond its Exp4 per-attack-type table.
- Re-check the venue of Uetz et al., "Can Risk-Based Alerting Mitigate Cybersecurity Alert Fatigue?" (arXiv:2609.02465): is the USENIX Security '27 acceptance confirmed?
- Check for papers on "shortcut learning" or "label leakage" in LLM security-alert or intrusion-detection benchmarks that would be the closest related work for A1.

Findings go in `notes/soc-alert-triage-prior-work.md`.

## Answer

**Verdict: kill criterion 3 does not fire.** Neither half has been done, as far as could be found, so both A1 and A2 stay.

- **(a) Non-LLM baseline or rule-name audit on SecAlertBench: not found.** The whole repo was read (README, all 23 scripts, the Exp4 table, all 16 prediction files): no non-LLM baseline. Exp4's script is named `rule_name` but groups by `attack_type`, and is LLM-only. Eight 2026 papers that cite or resemble the benchmark were searched by full text; none mentions it.
- **(b) LLM triage vs risk-based alerting on public data: not found.** Uetz et al. (arXiv:2609.02465) run no LLM experiment and only call for the comparison; the CATS repo has no LLM module. Closest work: Rieger et al. (ESWA 331, 2026) compare 8 LLMs with TF-IDF classifiers on 178 alerts from their own lab, with neither SecAlertBench nor RBA, and a linear SVM was best (F1 89.43%), so "simple models rival LLMs" exists at small scale.
- **Uetz et al. venue corrected:** the arXiv comment says "Submitted to USENIX Security '27"; author notification is 2026-12-03, so it is under review, not accepted. I re-checked this on the arXiv API myself and corrected the earlier gap-scan note and ticket.
- **SecAlertBench paper not found** (arXiv, Scholar, OpenAlex, Crossref, web): the repo's README names a paper but gives no ID, venue or authors. **This is the main residual risk:** the paper may contain a baseline or rule-level analysis that the repo omits. Re-check before submission.
- **Independent confirmation of the pilot:** the agent recomputed the headline numbers from the released files and found the same per-model 2,000-alert samples (zero alerts shared by all models) and the same fact that the LLM sees `rule_name`.
- **Closest related work for A1:** Arp et al. (USENIX Security 2022) pitfalls P4 (spurious correlations) and P6 (inappropriate baselines), read in full; Flood et al. (EuroS&P 2024), Yang et al. (USENIX Security 2024), Okafor (2026) were seen as abstracts only. Nothing found on rule-name leakage in alert triage; reviewers may read A1 as an applied Arp et al. pitfall.
- **Residual novelty risks:** the unread SecAlertBench paper; a competing LLM-vs-RBA preprint (the Uetz call and CATS data are public); "simple ML beats LLM" already existing in Rieger et al. "No paper does X" claims remain "not found", not proven.
