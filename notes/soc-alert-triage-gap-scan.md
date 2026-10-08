# Gap scan: LLM agents for SOC alert triage and log analysis

**Question:** Where is the strongest research gap in using LLMs or LLM agents to triage security alerts or analyse security logs, and is it feasible for us under the map's constraints (1 month, solo, 8 GB RAM + GTX 1650, <$30 API, no training, no human subjects)?

**Written:** 2026-10-08. Ticket: [01-gap-scan-soc-alert-triage](../.scratch/topic-search/issues/01-gap-scan-soc-alert-triage.md).

**Short answer:** The area is **crowded** at the level of "build an LLM/agent triage system" or "build a new SOC benchmark": we found 15+ papers and benchmarks from 2025–2026, most of them from the last 6 months. The one gap that is real, cheap and fits our constraints is an **evaluation flaw**: LLM triage results are reported without cheap non-LLM baselines. A one-hour pilot on the public SecAlertBench data (see 2) suggests a per-rule lookup table beats the reported average LLM by a wide margin. This gap is narrow, and one 2026 journal paper already shows ML baselines rivalling LLMs on a small dataset, so the novelty risk is medium.

---

## 1. Landscape

**Agentic investigation and SOC benchmarks (heavy, crowded):**

- **ExCyTIn-Bench**: LLM agents answer threat-investigation questions over 57 Microsoft Sentinel log tables; 7,542 questions; best model reward 0.606. arXiv:2507.14201 (v3 May 2026), accepted at ICML 2026. Code at github.com/microsoft/SecRL.
- **CORTEX**: multi-agent alert triage (behaviour-analysis, evidence-gathering and reasoning agents); releases production SOC investigation traces. arXiv:2510.00311 (Sep 2025).
- **CyberSOCEval** (Meta + CrowdStrike, part of CyberSecEval 4): malware-analysis and threat-intelligence reasoning benchmarks for SOC; it does not cover alert triage. arXiv:2509.20166 (Sep 2025).
- **SIABENCH**: 160 scenarios (25 deep-analysis, 135 alert-triage), an autonomous agent, and 11 LLMs evaluated. arXiv:2603.06422 (Mar 2026).
- **SIR-Bench**: 794 incident-response cases from 129 anonymised incident patterns, replayed in the cloud; adversarial LLM-as-judge; baseline agent 97.1% TP detection and 73.4% FP rejection; public release not stated. arXiv:2604.12040 (Apr 2026).
- **AuditBench**: four log-investigation tasks over Linux and Windows audit logs, 50+ scenarios, 5 frontier LLMs. arXiv:2606.10281 (Jun 2026, revised Sep 2026).
- **Towards Agentic Investigation of Security Alerts**: constrained-tool workflow (SQL over Suricata logs, grep) beats the same LLM without the workflow. arXiv:2604.25846; IEEE BigData 2025.

**Alert true/false-positive classification (closest to our gap):**

- **SecAlertBench**: 8,322 alerts from the SOCs of three enterprises (IDS/IPS, WAF, traffic inspection); 241 alert types; binary labels (2,496 Attack, 5,826 Non-Attack); 16 LLMs evaluated; average TPR 79.71%, F1 70.92%, **FPR 44.13%**. Its README mentions **no rule-based, majority or ML baseline**. Artifact: github.com/Dxsssu/SecAlertBench (repo created Apr 2026). We could not find the paper's arXiv ID or venue.
- **Rieger et al.**, "Possibilities and limitations of using LLMs for alert classification and prioritisation in SOCs": 8 LLMs (OpenAI, DeepSeek, Ai2) on **178** manually labelled alerts, compared with LR, RF and Linear SVM. Linear SVM had the best F1, and LLM prioritisation precision was low. *Expert Systems with Applications* 331 (2026), doi:10.1016/j.eswa.2026.133194.
- **Schärmer, Landauer, Skopik et al.**, "Let the Alerts Speak": ChatGPT and Gemini classify IDS alerts (attack vs FP) and map them to techniques; few-shot examples and system logs help. ARES 2026 Workshops, LNCS, doi:10.1007/978-3-032-35579-9_19. We read only the Crossref abstract; the authors are the AIT-ADS creators, so the paper likely uses AIT data (unverified).
- **AIDR**: compressed reasoning chains for alert triage, with a cloud-edge model split. arXiv:2512.08169 (Dec 2025).
- **Khanna et al. (CrowdStrike)**: reasoning LMs for endpoint-detection triage with RL, self-training and a calibrator; 82.6% accuracy on **private** human-labelled data. arXiv:2607.28460 (Jul 2026).

**Log → ATT&CK mapping:**

- **RHINO**: three-phase guided reasoning that maps network logs to ATT&CK; 86–88% accuracy. arXiv:2510.14233 (Oct 2025).
- **Security Logs to ATT&CK Insights**: Suricata logs → ATT&CK techniques → attacker cognitive traits. arXiv:2510.20930 (Oct 2025).

**Adversarial robustness of LLM log analysis (crowded since mid-2026):**

- **Poisoning the Watchtower**: prompt injection through attacker-controlled log fields; gpt-4o-mini; defences cut injection success from 26.6% to 11.8%. arXiv:2605.24421 (May 2026).
- **LogInject-1.0**: 12,847 log entries, 2,569 of them adversarial; up to 88.2% attack success against three production LLMs. arXiv:2607.14493 (Jul 2026).

**Non-LLM alert triage (the baselines LLM papers skip):**

- **Uetz et al.**, "Can Risk-Based Alerting Mitigate Cybersecurity Alert Fatigue?": the CATS suite, eight labelled alert datasets (seven public), and AUROC µ=0.92 across datasets. It states that LLM-based approaches "should be evaluated against RBA as a baseline and clearly demonstrate that their additional cost is justified" (§8). arXiv:2609.02465 (2 Sep 2026); "Submitted to USENIX Security '27" per the arXiv comment (under review, not accepted; checked 2026-10-08).
- **PACT**: active learning over an XGBoost screener on AIT-ADS and BOTSv1. arXiv:2605.22324 (May 2026; submitted to ACSAC 2026).
- **Survey**: Ndichu et al. synthesise 119 records (2015–2026) and name gaps in "operational validation, adversarial robustness, cross-environment generalization, and evaluation practice". arXiv:2605.08316 (May 2026; submitted to ACM CSUR).

## 2. Gap evidence

**Strongest gap (flawed evaluation): LLM alert-triage results are reported without cheap baselines, and public alert labels may be largely predictable from rule identity alone.**

What sources say:

- SecAlertBench reports LLM averages (F1 70.92%, FPR 44.13%), and its README lists no non-LLM baseline (SecAlertBench repo).
- Uetz et al. explicitly ask that LLM triage be compared with RBA, and they find RBA strong on public data (arXiv:2609.02465 §8). We found no paper that has done this comparison, which is unsurprising since their paper is five weeks old.
- Rieger et al. find that simple ML matches or beats LLMs, but on only 178 alerts, with no public dataset named in the abstract and no comparison with RBA or rule priors (doi:10.1016/j.eswa.2026.133194).

**Our own pilot (interpretation, not from a source):** we downloaded `secalertbench.json` (8,322 alerts) and ran a trivial baseline. It predicts the majority label of the alert's `rule_name`, learned on the training folds, under 5-fold random cross-validation with 3 seeds.

| Metric | Rule-name majority (ours, 5-fold) | SecAlertBench reported LLM average |
|---|---|---|
| Accuracy | 0.936 | n/a |
| TPR | 0.88–0.89 | 0.797 |
| FPR | 0.042 | 0.441 |
| F1 | 0.89 | 0.709 |

Supporting counts:

- 210 of 241 rules carry only one label. These single-label rules cover 4,851 of 8,322 alerts (58%).
- The 31 mixed-label rules cover the other 3,471 alerts, and the in-sample per-rule majority is 86.4% accurate on them. One rule alone has 1,432 alerts (1,403 Non-Attack, 29 Attack).
- 2,489 alerts share an identical (rule, method, URI, parameter, body, status) key with another alert, so few-shot or retrieval setups risk near-duplicate leakage.

Caveat: this baseline is supervised and in-distribution, while the LLMs are zero- or few-shot, so this is **not** a like-for-like comparison. What it shows is that (a) the benchmark lacks the obvious reference point and (b) any real triage ability has to be measured on the **mixed-label subset** and under **rule-grouped splits**. We have not read the SecAlertBench paper, which may stratify its results.

**Searches that did not find this already covered:**

- "LLM alert triage benchmark shortcut rule name baseline label leakage": only SecAlertBench and SIABENCH came back, neither of which audits shortcuts.
- "risk-based alerting large language model alert prioritization comparison": only Uetz et al. (no LLM experiments) and Rieger et al. (ML baselines, not RBA).
- "LLM alert triage compared against non-LLM baseline AIT-ADS": only Rieger et al. and the ARES paper.
- "SecAlertBench … arXiv": no paper or follow-up found, only the repo.
- "arXiv 2026 LLMs classify Suricata Wazuh IDS alerts true false positive public dataset": no RBA or rule-prior comparison found.

**Rejected sub-areas (crowded or infeasible):**

- **Agentic investigation benchmarks** (ExCyTIn, SIR-Bench, SIABENCH, AuditBench, CORTEX): heavy environments, frontier-model costs, and 5+ papers in 12 months.
- **Prompt injection through logs**: two 2026 preprints already cover it (arXiv:2605.24421, arXiv:2607.14493).
- **Log → ATT&CK mapping**: at least 3 recent works (RHINO, arXiv:2510.20930, the ARES paper), and ground truth is scarce.

## 3. Candidate problems

1. **Rule-prior shortcut audit.** On public alert-triage benchmarks, how much of LLM triage performance is explained by alert-rule identity? How do small and API LLMs compare with rule-prior, severity and simple-ML baselines on the mixed-label "hard" subset and under rule-grouped (unseen-rule) splits?
2. **LLMs vs risk-based alerting.** Do zero-shot LLM triage scores (single-alert, and with host or entity context windows) beat RBA and rule-level baselines on the seven public CATS alert datasets, measured by AUROC and by FP burden at fixed recall, and at what token cost?
3. *(Variant, weaker)* **Context window.** Does giving an LLM the RBA-style context (other alerts on the same entity within a window) close the gap to RBA? This could be an extra arm of #2. The ARES paper already reports that context helps, so on its own it is not novel.

Recommendation: merge #1 and #2 into one evaluation paper, along the lines of "Are LLM alert triagers better than cheap baselines?", run on SecAlertBench plus 3–4 CATS datasets.

## 4. Data and environments

| Dataset | Size | Labels | Licence | Access |
|---|---|---|---|---|
| **SecAlertBench** (github.com/Dxsssu/SecAlertBench) | 8,322 alerts; ~21.7 MB JSON | Per-alert `Attack`/`Non-Attack`; 241 `rule_name` values; 23 `attack_type` values | **No licence file** (GitHub API: licence null) | Public JSON, verified by download. Fields are HTTP request/response, IPs, ports, rule name and kill chain. Rule names and attack types are **in Chinese** (observed). |
| **CATS datasets** (github.com/962012d09b/cats, `/datasets`) | Seven public JSONL datasets, from 170 to 23,116 alerts each (see below) | Each alert labelled true or false (Uetz et al. §6) | **No licence file** (GitHub API: licence null) | Zip archives in the repo. Proprietary ERPCorp is excluded. CATS app runs via Docker Compose (Flask backend); it includes a batch processor for pipelines. |
| **AIT-ADS** (zenodo.org/records/8263181) | 2,655,821 alerts (Wazuh 2,293,628; Suricata 306,635; AMiner 55,558); 96.2 MB | Attack-phase **time windows** in `labels.csv`, not per-alert labels | CC-BY-4.0 | Landauer et al., CSET 2024. CATS ships per-alert-labelled subsets of one scenario. |
| **ExCyTIn-Bench** (github.com/microsoft/SecRL) | 57 log tables; 7,542 questions | Q&A with answers | arXiv page shows CC BY 4.0 (probably the paper's licence; repo licence not checked) | Too heavy for our environment. |

CATS dataset sizes (from Uetz et al., Table 3):

| Dataset | Alerts | Base rate |
|---|---|---|
| DEDALE Sigma | 1,819 | 3% |
| AIT-ADS Wazuh | 23,116 | 33% |
| AIT-ADS Suricata | 9,186 | 1% |
| SOCBED Sigma | 172 | 21% |
| SOCBED Suricata | 170 | 81% |
| APT29S2 Sigma | 13,861 | 98% |
| APT29S2 Suricata | 453 | 31% |

## 5. Smallest useful version (7–10 days)

- **Days 1–2:** Build a loader for SecAlertBench and 3–4 small or medium CATS datasets (SOCBED ×2, APT29S2 Suricata, DEDALE Sigma, AIT-ADS Suricata). Implement the baselines:
  - rule-majority, under random and rule-grouped splits;
  - rule level / severity;
  - TF-IDF + logistic regression;
  - RBA scores from the CATS batch processor, or a re-implementation of its Accumulation and Variety modules.
- **Days 3–6:** Run zero-shot triage with 2–3 quantized open models of ≤4B parameters locally (Ollama), producing a verdict plus a confidence score for AUROC. Inputs: the SecAlertBench mixed-label subset (3,471 alerts) plus a 1,000-alert stratified sample of single-label rules, and the small CATS sets in full. Run one cheap API model on a ~1,000-alert subset.
  - Rough token estimate: ~500 tokens per alert, so 5k alerts is about 2.5M input tokens. Check current API prices before running.
  - Local throughput on the GTX 1650 is unmeasured. A smoke test should time it.
- **Days 7–8:** Analysis: full set vs hard subset, random vs grouped splits, FP burden at fixed recall, and cost per 1k alerts.
- No training, no fine-tuning and no human subjects. Fitting LR or majority baselines is classical ML and fits the "no training" rule in spirit (no model weights are trained). Confirm this with the professor.

## 6. Risks

- **Crowding.** At least 10 directly relevant preprints appeared from Apr–Sep 2026 (SIR-Bench, AuditBench, SIABENCH, LogInject, Poisoning the Watchtower, Khanna et al., the ARES paper, Rieger et al., Uetz et al., the survey). Someone may publish "LLM vs RBA" soon after Uetz et al. The "ML baselines rival LLMs" message already exists at small scale (Rieger et al.), so our novelty has to come from rule-prior shortcuts, grouped splits, RBA and public data.
- **Unknown paper content.** We have not read the SecAlertBench paper itself, and it may already stratify by rule. Find and read it before committing.
- **Licences.** Neither the SecAlertBench nor the CATS repo has a licence. Research use with citation is likely fine, but redistribution is not; email the authors if we republish derived data.
- **Language.** SecAlertBench rule names and attack types are in Chinese. Small English-centric models may be handicapped, which confounds the results. Translate the rule names, or use multilingual models (e.g. the Qwen family).
- **Metric mismatch.** RBA prioritises entities over time, while LLMs judge single alerts. We must convert LLM verdicts to scores and compare with AUROC and FP burden per alert.
- **Label noise.** AIT-ADS labels come from time windows, so benign alerts inside attack windows may be mislabelled. CATS re-labels them; check how.
- **Hardware.** The 8 GB RAM and 4 GB VRAM limits allow ≤4B quantized models only. Results may then say little about frontier models, so a single API model is needed as a reference.

## 7. Scores (1–5)

Scores are for the merged candidate (#1 + #2).

| Criterion | Score | Justification |
|---|---|---|
| Gap strength | 4 | A concrete, measured flaw (no baselines; rule-only lookup beats the reported LLM average), plus an explicit call for this comparison in a USENIX Sec '27 paper. |
| Novelty | 3 | No one has found the rule-prior shortcut or compared against RBA, but "simple ML ≈ LLM" is already published at small scale (ESWA 2026). |
| Feasibility | 5 | Basic Python, JSON data, ≤4B local models, no training; the pilot baseline already ran in minutes. |
| Data availability | 4 | Two public labelled alert sources (SecAlertBench, CATS ×7) plus AIT-ADS (CC-BY). The missing repo licences and Chinese fields cost a point. |
| Cost | 5 | Mostly local inference; one API subset at an estimated few dollars. |
| Speed to results | 4 | Baseline numbers exist on day 1; LLM runs depend on unmeasured GTX 1650 throughput. |

## Takeaways (our interpretation)

- Do not build another triage agent or another SOC benchmark. That space is saturated by well-resourced teams (e.g. Microsoft for ExCyTIn, Meta/CrowdStrike for CyberSOCEval) and needs environments and budgets we lack.
- Our best angle is an **evaluation-practice paper**: cheap baselines plus a shortcut audit on public data. It is a type (ii) gap ("demonstrably flawed existing evaluation") under the map's definition.
- **Verdict:** pursue as a strong but medium-novelty candidate. It is feasible and fast, the gap is real but narrow, and its value depends on moving quickly, before RBA-vs-LLM comparisons appear.

## Unverified leads

These came up in search results but we did not open the primary source in this session:

- CORTEX listed at NeurIPS 2025 (neurips.cc virtual site, poster 137134). The venue is not confirmed.
- Roy & Balde, "Toward Context-Aware Alert Classification in SOCs Using LLMs", IEEE ICAIC 2026, doi:10.1109/icaic67076.2026.11395735. We saw Crossref metadata only, without an abstract.
- CyberSleuth (arXiv:2508.20643, a blue-team agent for web-attack forensics) and AttackSeqBench (arXiv:2503.03170, attack sequences in CTI reports). Seen only in search snippets.
- Splunk BOTS v1–v3 datasets: Splunk blog says v3 was released under an open-source licence. This is a vendor signal and was not checked. A university thesis from Turku, "Evaluation of LLM Agents for the SOC Tier 1 Analyst Triage Process", was also seen but not opened.
- LogAtlas (arXiv:2602.06777) and Policy-Guided Threat Hunting (arXiv:2603.23966): we read their abstracts, but they are peripheral (anomaly detection and hybrid DRL, not LLM triage evaluation). We did not check whether their datasets are public.
- Whether "Let the Alerts Speak" (ARES 2026) uses AIT-ADS, and whether it compares against non-LLM baselines.

## Sources

- arXiv:2507.14201: Wu et al., ExCyTIn-Bench (ICML 2026). https://arxiv.org/abs/2507.14201
- arXiv:2510.00311: Wei et al., CORTEX. https://arxiv.org/abs/2510.00311
- arXiv:2509.20166: Deason et al., CyberSOCEval. https://arxiv.org/abs/2509.20166
- SecAlertBench artifact. https://github.com/Dxsssu/SecAlertBench (and the GitHub API repo metadata)
- arXiv:2603.06422: Jajodia et al., SIABENCH. https://arxiv.org/abs/2603.06422
- arXiv:2604.12040: Begimher et al., SIR-Bench. https://arxiv.org/abs/2604.12040
- arXiv:2606.10281: Anand et al., AuditBench. https://arxiv.org/abs/2606.10281
- arXiv:2604.25846: Eilertsen et al., Towards Agentic Investigation of Security Alerts (IEEE BigData 2025). https://arxiv.org/abs/2604.25846
- doi:10.1016/j.eswa.2026.133194: Rieger et al., ESWA 331 (2026). https://eprints.glos.ac.uk/16399/
- doi:10.1007/978-3-032-35579-9_19: Schärmer et al., Let the Alerts Speak, ARES 2026 Workshops. Crossref abstract: https://api.crossref.org/works/10.1007/978-3-032-35579-9_19
- arXiv:2512.08169: Zhao et al., AIDR. https://arxiv.org/abs/2512.08169
- arXiv:2607.28460: Khanna et al., Cybersecurity Detection Classification with Reasoning-enabled LMs. https://arxiv.org/abs/2607.28460
- arXiv:2510.14233: Meng et al., RHINO. https://arxiv.org/abs/2510.14233
- arXiv:2510.20930: Hans et al., Security Logs to ATT&CK Insights. https://arxiv.org/abs/2510.20930
- arXiv:2605.24421: Pandey & Bhujang, Poisoning the Watchtower. https://arxiv.org/abs/2605.24421
- arXiv:2607.14493: Karanjai et al., LogInject / Context Contamination. https://arxiv.org/abs/2607.14493
- arXiv:2609.02465: Uetz et al., Can Risk-Based Alerting Mitigate Cybersecurity Alert Fatigue? (submitted to USENIX Security '27, under review); full PDF text read. https://arxiv.org/abs/2609.02465
- CATS repository and datasets. https://github.com/962012d09b/cats
- arXiv:2605.22324: Ndichu et al., PACT. https://arxiv.org/abs/2605.22324
- arXiv:2605.08316: Ndichu et al., AI-Driven Security Alert Screening survey. https://arxiv.org/abs/2605.08316
- AIT Alert Data Set, Zenodo record 8263181 (Landauer, Skopik, Wurzenberger, CSET 2024). https://zenodo.org/records/8263181
- arXiv:2602.06777: Chagna & Goldschmidt, LogAtlas. https://arxiv.org/abs/2602.06777
- arXiv:2603.23966: Sahay et al., Policy-Guided Threat Hunting. https://arxiv.org/abs/2603.23966
