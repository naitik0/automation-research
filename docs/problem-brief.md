# Problem brief: Robustness of LLM security-alert triage evaluation to simple baselines and label-revealing metadata

**Status:** approved 2026-10-08 · Naitik (solo MCA project)
**Evidence:** [pilot](../notes/soc-alert-triage-pilot.md) · [prior-work check](../notes/soc-alert-triage-prior-work.md) · [gap scan](../notes/soc-alert-triage-gap-scan.md) · [venues](../notes/venue-shortlist.md)

## Research question

**How robust are reported LLM alert-triage results once simple non-LLM baselines and potentially label-revealing alert metadata are controlled for?**

- **RQ1:** How do published zero-shot LLM triage results compare with simple non-LLM reference baselines on the same alerts, and how predictive of the label is rule identity on its own?
- **RQ2:** How does LLM triage performance change when potentially label-revealing fields are removed from the prompt?
- **RQ3:** How do LLMs and a content-based supervised baseline perform on alerts from rules unseen in training?
- **RQ4 (secondary, optional):** How do zero-shot LLMs compare with risk-based alerting (RBA) for alert prioritisation?

## Why it matters

SOCs face more alerts than analysts can review, and LLMs are proposed for Tier-1 triage, the decision whether an alert is a real attack. Benchmark results guide that adoption. They can overstate or misplace LLM capability in two ways: if no simple reference point is reported, or if part of the score comes from fields that already encode the label. Arp et al. name both risks in ML security evaluation: spurious correlations (P4) and inappropriate baselines (P6) [1].

## Gap evidence

- **SecAlertBench reports no non-LLM baseline.** The benchmark has 8,322 real SOC alerts from three enterprises and evaluates 16 LLMs, with average TPR 79.71%, FPR 44.13% and F1 70.92% [2]. Its released code and results contain no non-LLM baseline. Its per-type analysis ("Exp4") covers LLMs only. Its prompt gives the LLM the whole alert, including `rule_name`, `attack_type` and `kill_chain_all` [2]. Only the repository was found, not the paper.
- **Rule identity may be label-revealing.** 210 of the 241 rules carry only one label in the dataset [2, our count]. Only 31 rules, covering 3,471 alerts, carry both labels.
- **RBA has been proposed as the reference, but not yet tested against LLMs.** Uetz et al. write that "more computationally expensive approaches (especially those involving machine learning, including large language models) should be evaluated against RBA as a baseline" (§8). Their CATS suite covers eight labelled alert datasets, seven of them public. They run no LLM experiment themselves [3].
- **Closest work.** Rieger et al. find that a linear SVM (F1 89.64%) outperforms the best of eight LLMs (85.84%) on 178 alerts from their own lab [4]. They use no public benchmark and no RBA, and they don't examine label-revealing fields.
- **What we searched and didn't find:** baselines on SecAlertBench, LLM triage compared with RBA, and rule-name shortcuts in LLM alert triage. We searched arXiv, Google Scholar, OpenAlex, Crossref and the web, and ran full-text searches of ten related 2026 papers (queries in the prior-work note).

## Feasibility check (pilot, 2026-10-08)

- **The published results reproduce.** Each model was scored on its own random balanced sample of 2,000 alerts, not on all 8,322. The published 16-model headline averages are consistent with the 15 per-alert prediction files available for analysis plus the published summary metrics for the 16th model.
- **Prediction files available:** the benchmark releases one per-alert prediction file for each of its 16 models. 15 are available for our analysis. The 16th (`gemini-3-flash-preview.json`) is deleted by Windows Defender on our machine because its alerts contain real exploit strings. Only its summary metrics (read from the first 2.5 KB of the file) are available, not its per-alert predictions. So per-alert analyses use 15 models; the 16th is added only if the file can be opened safely, for example in a sandbox or VM.
- **Rule identity is highly predictive of the label.** A rule-identity reference reaches F1 0.898, TPR 0.844 and FPR 0.036. It is a diagnostic that predicts each rule's majority label in the training data. We trained it on the alerts outside each published sample and scored it on that sample. The published LLM averages are F1 0.709, TPR 0.797 and FPR 0.441. On the mixed-label rules the reference reaches F1 0.763.
  - **This is not a head-to-head result.** The reference is *supervised*: it learns the label of each rule from about 6,300 labelled alerts. The LLMs are *zero-shot*: they see the rule name but have never seen a label.
  - **What it shows** is how much label information rule identity carries, and therefore how much of a benchmark score could come from it. It is not evidence that LLMs are worse than a lookup table.
- **The data is usable.** Predictions match alerts by content (the files have no IDs). Two CATS datasets load with per-alert labels.
- **The local model runs, and F1 alone would mislead.** Qwen3-4B on our GTX 1650 takes 9.0 s per alert (95% CI 7.8–10.2 s). Zero-shot, it labelled all 118 alerts it was given as "Attack".

## Approach

**A1 (core contribution)** uses SecAlertBench.

1. **References vs published results (RQ1).** Evaluate on each of the 15 available models' published samples (about 2,000 alerts each), alongside that model's own predictions. The references are:
   - always "Attack";
   - the **rule-identity reference** (diagnostic): each rule's majority label in the training data. A test alert whose rule doesn't appear in the training data is predicted **Non-Attack**. That label is fixed in the implementation, not computed per sample. It is also the training-set majority label in every sample: about 4,810 Non-Attack vs 1,450 Attack. This affects 25–45 of the roughly 1,985 test alerts per sample. If a rule has an exactly balanced training set (a tie), the reference predicts Attack;
   - **TF-IDF + logistic regression** on the alert text.

   **Out-of-sample protocol:** the two supervised references are never trained on the alerts they are scored on. For each model's sample, they are trained only on the dataset alerts outside it (about 6,300, with content-duplicates of the sample's alerts removed) and scored only on the sample.

   This needs no LLM calls. The supervised references measure how much label information the data carries; they are not a fair contest with zero-shot models.
2. **Three information conditions (RQ2).** Run every model on one fixed, shared sample of 1,000 alerts (500 Attack, 500 Non-Attack, over-representing the mixed-label rules), with these prompts:
   - (a) the full benchmark prompt;
   - (b) `rule_name` removed;
   - (c) `rule_name`, `attack_type` and `kill_chain_all` removed.

   The models are Qwen3-4B and Llama 3.2 3B (local), and gpt-oss-120b and Claude Haiku 4.5 (API). Every condition uses the same alerts, so conditions are compared within each model.
3. **Unseen rules (RQ3).**
   - **Splits:** the 8,322 alerts are split into five folds by rule, so all alerts of a rule fall in the same fold.
   - **Baseline:** in each fold, TF-IDF + logistic regression is trained **only on the four training folds** and evaluated **only on the held-out fold**, whose rules it has never seen. Each alert is held out exactly once. The rule-identity reference can't predict an unseen rule, so it isn't used here.
   - **LLMs:** their step-2 predictions are scored fold by fold on the held-out alerts those predictions cover. This needs no extra calls.
4. **Metrics.** Report TPR (recall), FPR, precision and F1, each with bootstrap confidence intervals. Report AUROC where a score exists: the baselines' probabilities, and the local models' token log-probabilities. The published predictions and the API models give hard labels only.
   - **F1 alone is insufficient.** On a 50/50 sample, answering "Attack" every time gives precision 0.5, recall 1.0 and F1 0.67, close to the published LLM average of 0.709, while its FPR is 1.0. Qwen3-4B did exactly this in the pilot. FPR is what measures the analyst burden that triage is meant to reduce.
5. **Supervision mismatch.** The method and limitations sections state that the baselines learn from labels while the LLMs don't. Supervised results are framed only as evidence of how predictive the data is, never as a contest.

**A2 (secondary, optional if time is limited)** compares zero-shot LLM scores with RBA scores from the CATS batch processor (CPU only) on the two SOCBED datasets (170 and 172 alerts), using full prompts. It reports AUROC and false positives at fixed recall. A2 is dropped entirely if A1 runs late.

**Language.** Until RQ2 and RQ3 show an effect, the paper says "potential shortcut information" or "label-revealing metadata", not "leakage".

## Planned workload and budget

| Experiment | Alerts × models × conditions | LLM calls | Local compute | API cost |
|---|---|---|---|---|
| A1 step 1: references vs published predictions | about 2,000 × 15 available (of 16 published) × 1 | 0 | CPU minutes | $0 |
| A1 step 2: information conditions, local | 1,000 × 2 × 3 | 6,000 | 15.0 h (17.0 h at CI upper bound) | $0 |
| A1 step 2: information conditions, API | 1,000 × 2 × 3 | 6,000 | none | about $5.50 (Haiku $4.00, gpt-oss $1.50) |
| A1 step 3: grouped splits | reuses step 2 | 0 | CPU minutes | $0 |
| **A1 total** | | **12,000** | **15–17 h** | **about $5.50; $11 with a 2× margin** |
| A2 (optional) | 342 × 4 × 1 | 1,368 | 1.7 h | under $1 |

**How the costs were estimated:**
- **Local time:** the pilot's 9.0 s per alert (10.2 s at the CI upper bound). Llama 3.2 3B is smaller than Qwen3-4B and is assumed to be no slower; that's not yet measured.
- **Prompt size:** about 1,000 tokens per call, measured in the pilot, budgeted at 1,300 to allow for a different tokenizer.
- **Haiku 4.5:** $1 / $5 per million input/output tokens.
- **gpt-oss-120b on Groq, paid tier:** $0.15 / $0.60, budgeting 500 output tokens for its reasoning. The free tier, at about 150 calls a day, is too slow for 3,000 calls.

**Fit.** The worst case, A1 plus A2 with the 2× margin, is about $12 of the $20–30 budget and about 19 h of unattended laptop compute, which can run overnight across days 3–6. The schedule:

| Days | Work |
|---|---|
| 1–2 | Step 1 (no calls) |
| 3–6 | Information-condition runs; API runs should take hours (rate limits not yet checked) |
| 7–8 | Grouped splits and analysis |
| 9–10 | A2, or slack if A1 runs late |

That gives results within the 7–10 days and leaves the rest of the month for writing. Target: an 8–10 page paper for AI-SEC 2027 (due 10 Dec) or AsiaCCS 2027 cycle 2 (due 11 Dec), with arXiv as the fallback.

## Risks

- **Unread SecAlertBench paper.** The paper (not found) may already report a baseline or a rule-level analysis that its repository omits. Re-search before writing, and email the repository owner.
- **Competition.** A competing LLM-vs-RBA preprint may appear, since the call for that comparison and the data are public.
- **Weak local models.** Qwen3-4B labelled every pilot alert as an attack. Log-probability scores may still discriminate; if not, A1's model comparisons rest on the API models and the published predictions.
- **Non-English fields.** Rule names and attack types are in Chinese. We note this and include a multilingual model.
- **Licensing.** Neither dataset has a licence: research use with citation only, no redistribution.

## Rejected candidate problems

- **Effect of n8n's built-in defences on prompt-injection rates.** JAW already hijacks n8n templates through workflow inputs, so the core idea is covered and only a weak untested setting remains [5].
- **Runtime reliability of LLM steps in public n8n templates.** The gap is weak in a crowded area. The main n8n study is static [6], but the runtime reliability of agents is widely studied, and small local models handle multi-turn tool calling poorly.

## Fallback problem

**LLMs vs KICS on Docker Compose security misconfigurations, scored against hand-validated labels.**
- **Status:** KICS supports Compose files [7], and we found no LLM study of Compose.
- **When it applies:** it becomes the chosen problem only if a kill criterion fires (none has):
  1. the rule-identity reference can't reach F1 0.71;
  2. the data is unusable;
  3. both A1 and A2 already exist in prior work;
  4. the local runs exceed about 72 h.

## References

1. D. Arp, E. Quiring, F. Pendlebury, A. Warnecke, F. Pierazzi, C. Wressnegger, L. Cavallaro, K. Rieck. "Dos and Don'ts of Machine Learning in Computer Security." USENIX Security 2022. arXiv:2010.09470.
2. SecAlertBench artifact, "SecAlertBench: Evaluating Large Language Models for Tier-1 Alert Triage in Security Operations Centers." github.com/Dxsssu/SecAlertBench, commit 42a8488 (paper venue and authors not found).
3. R. Uetz, P. Bönninghausen, L. Hackländer-Jansen, M. Henze. "Can Risk-Based Alerting Mitigate Cybersecurity Alert Fatigue?" arXiv:2609.02465, 2026 (submitted to USENIX Security '27).
4. M. Rieger, A. Shah, A. Alam, M. J. Hossain. "Possibilities and limitations of using large language models (LLMs) for alert classification and prioritisation in security operations centers (SOCs)." Expert Systems with Applications 331, 2026. doi:10.1016/j.eswa.2026.133194.
5. N. Fendley, Z. Liu, A. Guan, J. Zhong, Y. Cao. "Comment and Control: Hijacking Agentic Workflows via Context-Grounded Evolution." arXiv:2605.11229, 2026.
6. Y. Tang, Y. Zhou, H. Chen. "Characterizing Large Language Model Agentic Workflows: A Study on N8n Ecosystem." arXiv:2606.29116, 2026.
7. KICS documentation, "Platforms." docs.kics.io/latest/platforms.
