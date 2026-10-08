# Prior-work check: LLM alert triage vs cheap baselines (kill criterion 3)

**Question:** Does kill criterion 3 fire? That is, has any paper or preprint (up to 2026-10-08) (a) reported a non-LLM baseline (rule lookup, majority, ML) on SecAlertBench, or audited how much its labels can be predicted from the rule name; or (b) compared LLM alert triage with risk-based alerting (RBA) on public alert data such as the CATS datasets? Criterion 3 fires only if both have been done.

**Written:** 2026-10-08. Ticket: [09-prior-work-check-soc-alert-triage](../.scratch/topic-search/issues/09-prior-work-check-soc-alert-triage.md). Builds on [soc-alert-triage-gap-scan](soc-alert-triage-gap-scan.md), but every important claim below was re-checked against the original source, not against that note.

## Verdict

**Criterion 3 does not fire. Neither (a) nor (b) has been done, as far as we could find.**

- **(a) Non-LLM baseline or rule-name audit on SecAlertBench: not found.** The repository contains no non-LLM baseline code or results, and we could not find the paper itself. This is the weakest part of the verdict (see "What we could not verify").
- **(b) LLM triage vs RBA on public alert data: not found.** Uetz et al. run no LLM experiment; they call for exactly this comparison. No other paper we found cites or uses CATS.

## How each claim was checked

| Claim | Status | How |
|---|---|---|
| SecAlertBench repo contents, README text, dataset size/label counts, scripts, result files | **Verified by reading the source** | Downloaded README, git tree, all 23 `.py` scripts (scanned), `top5_attack_type_metrics.csv`, and all 16 RQ1 result JSONs from github.com/Dxsssu/SecAlertBench |
| Headline numbers (avg TPR 79.71%, FPR 44.13%, F1 70.92%) | **Verified (recomputed)** | Recomputed from the 16 released RQ1 files: mean TPR 0.7971, mean FPR 0.4413, mean per-model F1 0.7092 |
| Uetz et al.: abstract, §6 datasets, Table 4, §8 and §10 quotes, no LLM experiment, "submitted" status | **Verified by reading the source** | arXiv abstract page and full PDF text (`pdftotext`), plus keyword search of the whole text |
| USENIX Security '27 dates | **Verified by reading the source** | usenix.org call for papers |
| CATS repo: no LLM module, no licence, anonymous | **Verified by reading the source** | GitHub API repo metadata, git tree and README |
| Absence of SecAlertBench/CATS/RBA/Uetz mentions in HESP, REFINE, SIABENCH, Towards Agentic Investigation, PACT, survey, Khanna et al., SENTINEL-RL, Case-Level Verification, NeMo-Guardrails proxy | **Verified in full text by keyword search** | Downloaded PDFs, `pdftotext`, regex search for `SecAlertBench`, `risk-based`, `RBA`, `CATS`, `Uetz`, `rule name/id`, `majority`, `shortcut`. We did not read these papers end to end |
| Rieger et al. details (178 alerts, TF-IDF + LR/RF/Linear SVM, own lab data) | **Verified by reading the source** (abstract, method and results passages) | Open-access PDF at eprints.glos.ac.uk |
| Arp et al. pitfalls P4 and P6 | **Verified by reading the source** | arXiv PDF text |
| The SecAlertBench paper (authors, venue, baselines, rule-level discussion) | **Could not verify: paper not found** | See section 1 |
| Whether the SecAlertBench paper itself reports a baseline or rule-level analysis | **Could not verify** | Same |
| Flood et al. ("Bad Design Smells in Benchmark NIDS Datasets"), Yang et al. (USENIX Sec '24), Okafor (MLWA 2026), Schärmer et al. (ARES 2026), SALAD | **Only abstract or metadata seen** | Paywalled or abstract-only; see section 4 |
| Absence claims ("no paper does X") | **Not provable** | Search logs in the last section; coverage is limited to the tools we had |

---

## 1. The SecAlertBench paper

**What the repository says (verified):**

- The repo is described as "the Artifact for the paper 'SecAlertBench: Evaluating Large Language Models for Tier-1 Alert Triage in Security Operations Centers'" (README). The README contains the paper's abstract but **no arXiv ID, venue, DOI, authors or citation block**.
- Repo owner: GitHub user `Dxsssu`, profile affiliation "Huazhong University of Science and Technology, Wuhan" (GitHub API user record). Repo created 2026-04-30, last pushed 2026-05-03, no licence (GitHub API). Commit messages: "Initial commit", "Add SOC alert dataset, evaluation scripts and documentation", "Prepare SecAlertBench artifact release". Script paths and usage examples contain `/home/dongxunsu/`, which hints at the author's name, but that is our inference only.
- The repo owner's other repository, `Awesome-LLM4SecOps`, does not list SecAlertBench.

**Where we could not find the paper (all negative):** arXiv API (`all:SecAlertBench`, 0 results), Google Scholar (0 results), OpenAlex (title and full-text search, 0 results), Crossref (no match), Semantic Scholar (title search rate-limited; paper lookup by arXiv ID returned data for Uetz only), general web search (only the repo). **Arxiv ID, venue and author list are therefore unknown.** The README's artifact phrasing and the 2026-04/05 repo dates are consistent with a paper under submission or review, but we have no evidence of its status.

**Baselines and rule-level shortcuts in the repo (verified; not the paper):**

- The repo has **no non-LLM baseline**: none of the 23 Python scripts references sklearn, a majority/lookup baseline or any rule-based predictor, and `requirements.txt` lists only torch, transformers, accelerate, bitsandbytes, modelscope, huggingface-hub, matplotlib, numpy, requests and tqdm.
- **Exp4 is per `attack_type`, LLM-only.** `RQ2/Exp4/top5_attack_type_metrics.csv` has 35 rows: five attack types (code execution, sensitive information leakage, directory traversal, SQL injection, unauthorized access/permission bypass) times seven LLMs, with TPR, FPR and F1. The script `stats_rq2_exp4_rule_name_metrics.py` is named "rule_name" but groups by `attack_type` (verified in code). The README calls Exp4 "Alert-Type Generalization". Nothing there measures how predictable the label is from `rule_name`.
- The Exp2 "user-baseline" files are a prompt-wording variant of the LLM, not a non-LLM baseline (script `..._user_baseline_eval.py` only changes the prompt tag).

**Evaluation design that matters for A1 (verified from scripts and released results):**

1. The LLM is given the **whole record**, including `rule_name`, `attack_type` and `kill_chain_all` (`build_user_content` dumps all fields; the result records contain those keys). So the LLM can use the rule name, just as a lookup baseline does.
2. The headline numbers are **not on the full 8,322 alerts.** Each RQ1 result file has exactly **2,000 alerts: 1,000 Attack and 1,000 Non-Attack** (`--sample-per-class 1000`; all 16 files checked). The seed is optional (`default=None`), and the 16 models were evaluated on **different random samples**: pairwise overlap of alert records is 550–623 of about 1,985 unique records, and the intersection across all 16 is 0. The reported averages are means over those 16 independent balanced samples.
3. So the released RQ1 evaluation set is **50% Attack**, whereas the full dataset is 30% Attack (2,496 of 8,322, README). TPR and FPR are insensitive to this, but precision and F1 are not. **Our earlier pilot F1 of 0.89 was on the natural 30%-attack distribution and is not directly comparable with the 70.92% average F1.** TPR and FPR are the safer comparison (pilot 0.88–0.89 / 0.042 vs 0.797 / 0.441).
4. A single model's 2,000-alert sample contains 189 to 195 distinct rule names (checked for two models); the 241 figure is the README's count for the full dataset and we did not recompute it here.

## 2. Uetz et al. (arXiv:2609.02465): venue check

- **Verified:** arXiv listing "Submitted to USENIX Security '27", `cs.CR`, v1 dated 2026-09-02, authors Rafael Uetz, Philipp Bönninghausen, Louis Hackländer-Jansen, Martin Henze (Fraunhofer FKIE; Henze also RWTH Aachen). The comment says **submitted, not accepted**.
- **Verified:** the paper's Open Science section says the CATS repository "will be deanonymized and made publicly available in case of paper acceptance". The repo (`github.com/962012d09b/cats`, created 2026-04-22, last push 2026-05-26) is still an anonymous account, and its README still contains the placeholder `X.X.X.X:XXX`.
- **Verified:** the USENIX Security '27 call for papers lists Cycle 1 submission due 2026-08-25, early-reject notification 2026-10-06, **author notification 2026-12-03**; Cycle 2 due 2027-01-26. The conference page shows no accepted-papers list and neither "Uetz" nor "Risk-Based Alerting". An arXiv post on 2026-09-02 fits a Cycle 1 submission, so **acceptance cannot have been announced by 2026-10-08** and is not confirmed. (That the paper is in Cycle 1 is our inference; the paper does not say which cycle.)
- **Correction to the earlier note:** `soc-alert-triage-gap-scan.md` wrote "USENIX Security '27" without qualification and the scores table said "USENIX Sec '27 paper". Write it as "submitted to USENIX Security '27 (under review)" until 2026-12-03 or later.
- **Content relevant to us (verified in the PDF):**
  - The abstract ends: RBA "serves as a strong baseline for more complex, resource-intensive alert triage approaches (e.g., based on large language models)". §8 says such approaches "should be evaluated against RBA as a baseline and clearly demonstrate that their additional cost is justified". The conclusion repeats the recommendation. **The paper contains no LLM experiment.**
  - Eight datasets (Table 3), six created or extended by the authors; ERPCorp is proprietary and "all other datasets" are public. The CATS repo's `datasets/` folder holds eight zip files (AIT AMiner/Suricata/Wazuh, APT29 Sigma/Suricata, DEDALE Sigma, SOCBED Sigma/Suricata). Seven of them match the seven public datasets in Table 3; the extra AIT AMiner zip is not evaluated (the paper says it omitted AMiner alerts), so the earlier note's "seven public datasets" is correct.
  - A **"Rule Level"** (severity) prioritisation baseline is already in the paper: AUROC mean 0.72, std 0.21 across the eight datasets, versus 0.92 / 0.09 for the best RBA combination (abstract and Table 4). So severity-only baselines are not new.
  - The CATS backend `modules/` folder contains `accumulated_risk`, `aperiodicity`, `fixed_score`, `level_score`, `rarity`, `variety` only; no LLM module.
  - The CATS repo has no licence (GitHub API reports `license: null`).

## 3. Part (a): non-LLM baseline or rule-name audit on SecAlertBench

**Not found.** Evidence:

- The SecAlertBench repo itself has none (section 1).
- Full-text keyword search of recent LLM-triage preprints found no mention of SecAlertBench: HESP (arXiv:2609.33446), REFINE (arXiv:2609.32516), SENTINEL-RL (arXiv:2609.04159), SIABENCH (arXiv:2603.06422), Khanna et al. (arXiv:2607.28460), PACT (arXiv:2605.22324), the Ndichu survey (arXiv:2605.08316), Towards Agentic Investigation of Security Alerts (arXiv:2604.25846), Case-Level Verification (arXiv:2610.08406), NeMo-Guardrails proxy (arXiv:2610.09906).
- Searches for "SecAlertBench" in arXiv, Google Scholar, OpenAlex (title and full text), Crossref and the general web return only the repo.
- Because the SecAlertBench paper was not found, **we cannot rule out that the paper contains a baseline or rule-level analysis that the repo omits.** That is the main residual risk for (a).

**Nearest related work (partial overlap only):**

- **Rieger et al.**, *Expert Systems with Applications* 331 (2026), doi:10.1016/j.eswa.2026.133194 (available online 2026-06-15). Eight LLMs vs Logistic Regression, Random Forest and Linear SVM on TF-IDF features, 178 manually labelled alerts from the authors' own simulated lab (Wazuh and Suricata), stratified 5-fold CV. The Linear SVM had the best F1 (89.64% (corrected 2026-10-08 from the paper's results text; best LLM GPT-4.5-preview 85.84%)). It does not use SecAlertBench, does not audit rule identity as a predictor, and does not use RBA. The paper explicitly notes that large public SOC datasets were not used. Its priority ground truth is derived from the detectors' rule levels.
- **Schärmer et al.**, ARES 2026 Workshops, doi:10.1007/978-3-032-35579-9_19: LLM classification of IDS alerts, ChatGPT and Gemini. Only the Crossref abstract was readable (full text behind a login). We cannot say which dataset or baselines it uses.

## 4. Part (b): LLM triage vs RBA on public alert data

**Not found.** Evidence:

- Uetz et al. have no LLM experiment (full-text search: "language model" appears only in the abstract, §1, §8 and §10 as a recommendation or contrast, and once in §4 where the authors used LLM queries to look for risk incident rules).
- The CATS repo has no LLM module (section 2).
- Semantic Scholar's citation list for arXiv:2609.02465 was empty on 2026-10-08 (the paper is five weeks old, so this is weak evidence).
- arXiv API queries for "risk-based alerting" return only Uetz et al. and an unrelated LLM-attack-detection paper (arXiv:2602.11247, "Peak + Accumulation", about scoring multi-turn LLM attacks, not SOC alerts; abstract-level only).
- The Ndichu survey (May 2026) predates Uetz et al. and says peer-reviewed evaluation of commercial RBA "remains limited" (survey §3.2.3; full text keyword hit).
- Google Scholar queries combining "risk-based alerting", "large language models" and CATS return only Uetz et al. and the Ndichu survey.

## 5. Closest related work on shortcut learning and label leakage

No paper found audits rule-name or rule-ID leakage for LLM or ML alert triage. The nearest work is general:

- **Arp et al.**, "Dos and Don'ts of Machine Learning in Computer Security", USENIX Security 2022 (arXiv:2010.09470). Defines **P4 Spurious Correlations**: "Artifacts unrelated to the security problem create shortcut patterns for separating classes", and **P6 Inappropriate Baselines**. Surveys 30 papers; spurious correlations are one of the pitfalls found across papers. *(Verified in full text.)* This is the right citation framing for A1, but it is generic and does not address LLM alert triage.
- **Flood, Engelen, Aspinall, Desmet**, "Bad Design Smells in Benchmark NIDS Datasets", IEEE EuroS&P 2024, doi:10.1109/EuroSP60621.2024.00042. Manual analysis of seven benchmark NIDS datasets and six "design smells" such as ambiguous ground truth and labelling inaccuracies. *(Bibliographic data verified with Crossref; the findings come from a search-result summary only, we did not read the paper.)*
- **Yang et al.**, "True Attacks, Attack Attempts, or Benign Triggers? An Empirical Measurement of Network Alerts in a Security Operations Center", USENIX Security 2024. 115 M alerts over four years; 49% "benign triggers" that "correctly matched security events but had business-justified explanations". Supports the view that alert labels depend on the deployment, not on the attack content alone. *(Abstract only. The earlier Awesome-LLM4SecOps list labels it "2025", but the USENIX page is the 2024 symposium.)*
- **Okafor**, "A leakage-free benchmark of offline policy learning for SOC alert triage", *Machine Learning with Applications* 2026 (doi:10.1016/j.mlwa.2026.100984, open access). Concerns **temporal leakage** in RL on UNSW-NB15 and CIC-IDS-2017 flow data; no LLMs and no rule identity. *(Abstract only, via OpenAlex's copy; the ScienceDirect page returned 403.)*
- **Rieger et al.** (above): simple ML matches or beats LLMs, but on 178 own-lab alerts.

## Takeaways (our interpretation)

- **Kill criterion 3 does not fire.** Both halves are open as far as we can tell. We keep A1 (rule-name audit on SecAlertBench) and A2 (LLM vs RBA on CATS).
- **A1 needs a design change.** The released SecAlertBench LLM results are on 2,000-alert balanced samples, independently drawn per model, and the LLM sees `rule_name`. A fair A1 should (i) score the rule-lookup baseline on the same kind of balanced sample and report TPR and FPR first, (ii) report F1 under both the balanced and the natural 30% prevalence, (iii) include a "rule name and attack type withheld" LLM arm if budget allows, and (iv) use rule-grouped splits. Our pilot's F1 of 0.89 must not be quoted next to the 70.92% average F1.
- **A2 is the more time-sensitive half.** Uetz et al. publicly invite the LLM-vs-RBA comparison and the CATS data are public, so anyone could run it. We should move quickly and treat any later arXiv listing as a scoop risk.
- **The paper-status caveat on Uetz et al. matters for citations.** Cite it as an arXiv preprint submitted to USENIX Security '27, not as accepted. The CATS repo is anonymous and unlicensed; confirm terms with the authors before redistributing anything.

## Residual novelty risks

1. **Unread SecAlertBench paper.** It may include a rule-level or non-LLM baseline analysis that the repo does not. The authors could also release a revision or follow-up with one. Re-search arXiv for the paper before submitting, and consider emailing the repo owner.
2. **Concurrent LLM-vs-RBA work.** The Uetz recommendation is explicit and the data are public; a competing group could post within weeks. Our searches cannot see unposted work.
3. **"Simple ML beats LLM" is not new.** Rieger et al. (ESWA 2026) already show it on small private data. Our contribution must rest on scale (public benchmarks), rule-identity shortcuts, grouped splits, and RBA.
4. **Search coverage.** The arXiv API keyword search is brittle (it missed papers whose titles we know), Semantic Scholar rate-limited us, and Google Scholar returned few results. Absence is "not found", not "does not exist".
5. **Generic shortcut-learning framing exists** (Arp et al. P4/P6, Flood et al.). A reviewer may call a rule-name audit a known pitfall applied to a new dataset; the value has to come from the measured effect on LLM triage claims.

## Searches run (2026-10-08)

Queries that did not find the gap covered are listed as well as those that found leads.

**SecAlertBench paper (all negative for the paper itself):**
- Web search: `SecAlertBench: Evaluating Large Language Models for Tier-1 Alert Triage in Security Operations Centers`; `"SecAlertBench" LLM alert triage 8,322 alerts 16 LLMs paper`; `"SecAlertBench" Su Huazhong University ... benchmark LLM`; `arXiv 2026 LLM alert triage "SecAlertBench"`. Only the GitHub repo returned.
- arXiv API: `all:SecAlertBench`, `abs:"Tier-1" AND abs:alert AND abs:LLM`, `all:"alert triage" AND all:benchmark AND all:LLM`, `all:SecAlertBench OR all:"Sec-Alert-Bench"`. 0, 0, 3 unrelated, 0.
- Google Scholar: `"SecAlertBench"` (no match), `"Tier-1 alert triage" LLM benchmark SOC baseline` (2 unrelated reviews), `LLM alert triage "rule name" OR "rule identity" shortcut baseline SOC benchmark` (2 unrelated).
- OpenAlex: `search=SecAlertBench` (0), full-text `SecAlertBench` (0), title search (unrelated results). Crossref bibliographic search (no match). Bing (nothing relevant). Semantic Scholar title search (HTTP 429).

**Part (a), non-LLM baseline / rule-name audit / shortcuts:**
- arXiv API: `abs:"alert" AND abs:"majority" AND abs:"baseline" AND abs:"LLM" AND abs:"SOC"` (1 unrelated), `abs:"alert" AND abs:"rule name" AND abs:LLM` (0), `abs:"shortcut" AND abs:"alert" AND abs:LLM AND abs:security` (0), `abs:"label leakage" AND abs:"intrusion detection"` (0), `abs:"shortcut learning" AND abs:"intrusion detection"` (1 unrelated), `abs:"LLM" AND abs:"alert" AND abs:"triage" AND abs:"non-LLM"` (0).
- Web search: `LLM SOC alert classification benchmark rule-based baseline outperforms LLM rule ID shortcut label leakage 2026` (leads: Okafor MLWA, Rieger, SALAD dataset, an unrelated internship repo discussing GUIDE leakage, not a paper). Google Scholar: `"alert triage" LLM "non-LLM" OR "simple baseline" OR "majority baseline" ...` (8 unrelated reviews/surveys).
- Full-text greps of the papers listed in section 3.

**Part (b), RBA vs LLM:**
- arXiv API: `all:"risk-based alerting"` (Uetz + 1 unrelated), `all:"CATS" AND all:"alert" AND all:"risk"` (Uetz only), `abs:"risk-based alerting" AND abs:"language model"` (Uetz only), `abs:"alert prioritization" AND abs:"large language model"` (Uetz only).
- Web search: `LLM alert triage compared with risk-based alerting baseline CATS datasets AUROC` (Uetz, an industry article, unrelated). Google Scholar: `"risk-based alerting" "large language models" alert triage CATS` (Uetz and the Ndichu survey).
- Semantic Scholar citations of arXiv:2609.02465: empty.

**Recent LLM-triage sweep (October 2026):** arXiv API `abs:alert AND abs:triage AND abs:language AND abs:model AND cat:cs.CR` (17 results, newest 2026-10-07), `abs:"security operations" AND abs:benchmark AND abs:alerts AND abs:LLMs AND cat:cs.CR` (7), `abs:"alert fatigue" AND abs:LLM AND cat:cs.CR` (11). None of the October 2026 results mentioned SecAlertBench, CATS or RBA in the abstract; the two we opened (arXiv:2610.08406, 2610.09906) have no relevant keyword hits in the full text.

**Shortcut / leakage related work:** arXiv abs pages and full text for Arp et al.; USENIX page for Yang et al.; Crossref for Flood et al.; Edinburgh thesis page for Flood; OpenAlex and Crossref for Okafor. Several title searches via the arXiv API returned 0 results even for known papers, so we fell back to other indexes.

## Sources

- SecAlertBench artifact: README, repository tree, scripts, `0x04. Evaluation Results/RQ1/*.json`, `RQ2/Exp4/top5_attack_type_metrics.csv`, GitHub API metadata. https://github.com/Dxsssu/SecAlertBench
- Dxsssu GitHub profile and repositories (GitHub API). https://github.com/Dxsssu
- arXiv:2609.02465: Uetz, Bönninghausen, Hackländer-Jansen, Henze, Can Risk-Based Alerting Mitigate Cybersecurity Alert Fatigue? (submitted to USENIX Security '27). https://arxiv.org/abs/2609.02465 and https://arxiv.org/pdf/2609.02465
- CATS repository (anonymous). https://github.com/962012d09b/cats
- USENIX Security '27 call for papers. https://www.usenix.org/conference/usenixsecurity27/call-for-papers
- USENIX Security '27 conference page. https://www.usenix.org/conference/usenixsecurity27
- doi:10.1016/j.eswa.2026.133194: Rieger, Shah, Alam, Hossain, ESWA 331 (2026). https://eprints.glos.ac.uk/16399/ (PDF read)
- doi:10.1007/978-3-032-35579-9_19: Schärmer et al., Let the Alerts Speak, ARES 2026 Workshops (Crossref abstract only). https://api.crossref.org/works/10.1007/978-3-032-35579-9_19
- arXiv:2609.33446: Liu, Wang, HESP. https://arxiv.org/abs/2609.33446
- arXiv:2609.32516: Chen, Long, Wang, REFINE. https://arxiv.org/abs/2609.32516
- arXiv:2609.04159: SENTINEL-RL. https://arxiv.org/abs/2609.04159
- arXiv:2603.06422: SIABENCH. https://arxiv.org/abs/2603.06422
- arXiv:2604.25846: Towards Agentic Investigation of Security Alerts. https://arxiv.org/abs/2604.25846
- arXiv:2605.22324: Ndichu et al., PACT. https://arxiv.org/abs/2605.22324
- arXiv:2605.08316: Ndichu et al., AI-Driven Security Alert Screening survey. https://arxiv.org/abs/2605.08316
- arXiv:2607.28460: Khanna et al. https://arxiv.org/abs/2607.28460
- arXiv:2610.08406: Sun et al., Case-Level Verification in Scanner-LLM Cascades. https://arxiv.org/abs/2610.08406
- arXiv:2610.09906: Constrained-Action AI Remediation for SIEM/XDR via a NeMo-Guardrails Proxy. https://arxiv.org/abs/2610.09906
- arXiv:2010.09470: Arp et al., Dos and Don'ts of Machine Learning in Computer Security (USENIX Security 2022). https://arxiv.org/abs/2010.09470
- doi:10.1109/EuroSP60621.2024.00042: Flood, Engelen, Aspinall, Desmet, Bad Design Smells in Benchmark NIDS Datasets (EuroS&P 2024); Crossref record only. https://api.crossref.org/works/10.1109/eurosp60621.2024.00042
- Yang et al., True Attacks, Attack Attempts, or Benign Triggers? (USENIX Security 2024), abstract only. https://www.usenix.org/conference/usenixsecurity24/presentation/yang-limin
- doi:10.1016/j.mlwa.2026.100984: Okafor, A leakage-free benchmark of offline policy learning for SOC alert triage (abstract via OpenAlex). https://api.openalex.org/works/doi:10.1016/j.mlwa.2026.100984
- SALAD: SOC Alert Labeled Analysis Dataset, Zenodo record 18912306 (metadata page only). https://zenodo.org/records/18912306
- arXiv:2602.11247: Peak + Accumulation (title-level only, judged unrelated).
