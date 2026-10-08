# Write and approve the problem brief

Type: task
Status: resolved
Blocked by: 06, 08, 09
Map: [Topic search](../map.md)
Findings: [docs/problem-brief.md](../../../docs/problem-brief.md)

## Question

Draft the 1–2 page problem brief for the chosen problem (research question, why it matters, gap evidence with citations, feasibility check, rough approach (A1 as the core experiment, A2 as the second), the rejected candidate problems B and C with reasons, and the fallback problem D with its kill criteria; see [Choose the problem](06-choose-the-problem.md)) and revise it until the user approves it. HITL: the user approves. Draft only if neither the feasibility pilot nor the prior-work check fired a kill criterion; if one did, the brief is written for the fallback problem instead. Save it as `docs/problem-brief.md`. Before a citation goes into the brief, re-open it and confirm the title, authors, and the claim it supports.

## Answer

**Approved by the user on 2026-10-08** after three revisions. The brief is `docs/problem-brief.md`.

- **Title:** "Robustness of LLM security-alert triage evaluation to simple baselines and label-revealing metadata".
- **Main research question:** how robust are reported LLM alert-triage results once simple non-LLM baselines and potentially label-revealing alert metadata are controlled for?
- **A1 (core contribution):** on SecAlertBench.
  - Published predictions from the 15 available models (of 16) are compared with three references, all trained out-of-sample: always "Attack"; a rule-identity reference, used as a diagnostic (unseen rule → Non-Attack, tie → Attack); and TF-IDF + logistic regression.
  - Three information conditions: full prompt; `rule_name` removed; `rule_name`, `attack_type` and `kill_chain_all` removed. These run on 1,000 shared alerts × 4 models (Qwen3-4B and Llama 3.2 3B locally, gpt-oss-120b and Claude Haiku 4.5 by API).
  - Unseen rules: grouped-by-rule five-fold splits, with TF-IDF + logistic regression trained only on the training folds.
  - Metrics: TPR, FPR, precision and F1, plus AUROC where scores exist.
- **A2 (secondary, optional):** zero-shot LLMs vs RBA on the two SOCBED datasets in CATS.
- **Workload:** 12,000 LLM calls for A1, about 15–17 h of local compute, and about $5.50 of API spend ($11 with a 2× margin).
- **Rejected:** the n8n defences and n8n runtime-reliability candidates. **Fallback:** Docker Compose vs KICS, behind four kill criteria, none of which fired.
- **Corrections found while re-opening the citations:** Rieger et al.'s best F1 is 89.64%, not 89.43% (fixed in the prior-work note and ticket); CATS has seven public datasets, not eight.

## Comments

- 2026-10-08: The user set the research design before drafting.
  - **A1:** published LLM results vs simple non-LLM baselines, and three information conditions (full prompt; `rule_name` removed; `rule_name`, `attack_type` and `kill_chain_all` removed). Unseen-rule generalisation uses grouped-by-rule splits with a TF-IDF + logistic regression baseline, not rule-majority. Metrics beyond F1, and AUROC where confidence scores exist. The supervised-vs-zero-shot mismatch is discussed explicitly.
  - **A2:** LLMs vs RBA on CATS, if time permits; can shrink to two datasets.
  - **Language:** say "potential shortcut information" or "label-revealing metadata", not "leakage", until the experiments establish it.
- 2026-10-08: First draft written to `docs/problem-brief.md`. Every citation was re-opened beforehand. That check corrected the Rieger et al. F1 to 89.64% (the prior-work note had said 89.43%). Awaiting the user's review.
- 2026-10-08: Revision 2, following the user's review:
  - **Framing:** neutral title; the main question is now about how robust the evaluation is once simple baselines and label-revealing metadata are controlled for.
  - **Rule-majority result:** presented as evidence of how predictive rule identity is, not as a head-to-head win, with the supervised-vs-zero-shot mismatch stated explicitly.
  - **F1:** the brief explains why F1 alone is insufficient (always-Attack scores F1 0.67 on a 50/50 sample).
  - **Workload:** an exact table, 1,000 alerts × 4 models × 3 conditions = 12,000 calls; local runs 15–17 h; API about $5.50, or $11 with a 2× margin.
  - **A2:** explicitly optional.
