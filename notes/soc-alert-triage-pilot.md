# Feasibility pilot: LLM alert triage vs cheap baselines (kill criteria 1, 2 and 4)

**Question:** Do kill criteria 1, 2 and 4 from [Choose the problem](../.scratch/topic-search/issues/06-choose-the-problem.md) fire for the chosen problem (SOC alert triage)? Criterion 3 is covered by [soc-alert-triage-prior-work](soc-alert-triage-prior-work.md).

**Written:** 2026-10-08. Ticket: [08-feasibility-pilot-soc-alert-triage](../.scratch/topic-search/issues/08-feasibility-pilot-soc-alert-triage.md). Started 19:53 IST, finished about 22:10 IST (about 2h15m of the 3-hour box, including a network outage and a memory-pressure stop). Scripts, commands, pinned versions and raw results are in [`pilot/`](../pilot/README.md).

## Verdict

| Criterion | Fires? | One-line reason |
|---|---|---|
| 1. Baseline | **No** | A rule-majority lookup reaches F1 0.898 on samples built like the benchmark's own, against 0.709 for the LLMs. |
| 2. Data | **No** | Predictions match alerts by content (99.8%), the paper's headline numbers reproduce exactly, and both CATS datasets load with labels. |
| 4. Time | **No** | The planned local runs project to about 24–27 h; the worst case is about 49 h against the 72 h threshold. |

None of the three fired, so A stays the chosen problem as far as this pilot goes. Four things the pilot found change how A1 must be run; they are under "Findings that shape the brief" below.

## What was done

### Criterion 1: rule-majority baseline (script `pilot/01_data_and_baseline.py`)

- **Data (verified by download, pinned commit):** `secalertbench.json` from github.com/Dxsssu/SecAlertBench at commit `42a8488…`: 8,322 alerts (2,496 Attack, 5,826 Non-Attack), 241 `rule_name` values. 210 rules carry one label, 31 carry both; those 31 cover 3,471 alerts.
- **The LLMs were not scored on all 8,322 alerts.** Each released RQ1 file has 2,000 alerts (1,000 Attack, 1,000 Non-Attack; the script's `--sample-per-class 1000`), and each of the 15 models we could read has its own random sample: overlap with another model's sample is about 550–610 alerts and no alert is in all 15. So the baseline was scored **per model, on that model's own sample**, training on the dataset rows that are not content-duplicates of that sample's alerts. An unseen rule is predicted Non-Attack.
- **Baseline result, averaged over the 15 model samples:** F1 **0.898** (bootstrap 95% CI 0.894–0.901), TPR **0.844**, FPR **0.036**.
- **LLM result, recomputed from the same files:** F1 0.696, TPR 0.784, FPR 0.454 (15 models). Adding Gemini's in-file summary (F1 0.871, TPR 0.969, FPR 0.256) gives F1 0.7092, TPR 0.7971, FPR 0.4413, which equals the abstract's 70.92% / 79.71% / 44.13%.
- **Mixed-label slice** (only alerts whose rule carries both labels; about 800 alerts per model): baseline F1 0.763, TPR 0.678, FPR 0.082 against LLM F1 0.578, TPR 0.661, FPR 0.521. The baseline still wins, by less.
- **Earlier pilot's number superseded:** the 0.89 F1 in the gap scan came from 5-fold cross-validation over the natural 30%-Attack distribution; the new 0.898 is on balanced samples like the LLMs' and is the figure to quote. A rerun of the old protocol gives F1 0.892 and FPR 0.044 (`baseline_cv5_random_full_set`).
- **Criterion 1 fires only if F1 < 0.71. It does not (0.898).**

### Criterion 2: data usability

- **Matching.** The released predictions were produced on records whose IP addresses differ from the released dataset (the README says IPs were replaced with random ones), so no row matches exactly and there is no alert ID. Matching on all fields except `sip`, `dip` and `xff` finds a dataset record for 1,995–2,000 of each model's 2,000 rows. About 70–90 rows per model are ambiguous because the dataset has duplicate records (101 duplicate keys, 218 records), but at most one row per model has a label conflict and none has a rule conflict. The analysis does not depend on the join, because each prediction row carries its own record, true label and rule name.
- **Recomputation.** Recomputed FPR matches each file's own summary to three decimals; the 16-model averages match the abstract (see above).
- **Gemini file.** `gemini-3-flash-preview.json` is removed by Windows Defender when written to disk (the alerts contain real exploit strings such as Log4j JNDI payloads), so only 15 of 16 prediction files were analysed. Gemini's in-file summary was read from the first 2.5 KB of the raw file. No Defender setting was changed. Anyone redoing this must expect the same removal.
- **CATS.** `socbed_suricata` (170 alerts: 138 misuse, 32 benign, 23 rules) and `socbed_sigma` (172 alerts: 36 misuse, 136 benign, 25 rules) load from the pinned commit `628cf48…` with a per-alert label in `metadata.misuse` (`pilot/02_cats_load.py`).
- **Criterion 2 fires only if predictions can't be reliably matched or CATS lacks per-alert labels. It does not.**

### Criterion 4: throughput (scripts `03_*.py`, `04_*.py`)

- **Setup:** portable llama.cpp b11509 (CUDA 13.4) and `Qwen3-4B-Instruct-2507-Q4_K_M.gguf` from `unsloth/Qwen3-4B-Instruct-2507-GGUF` (revision `a06e946…`, Apache-2.0), all layers on the GTX 1650 (3.8 of 4 GB VRAM), context 8,192, sequential requests, temperature 0. **Deviation from the ticket:** llama.cpp instead of Ollama, because Ollama is not installed and a portable build avoids a system-wide install.
- **Prompt:** SecAlertBench's own system prompt, alert formatting and parsing (the full alert JSON, including `rule_name` and `attack_type`), on a 100 Attack + 100 Non-Attack sample (seed 42).
- **The run covered 118 of the 200 planned alerts.** Claude Code stopped it because the machine was critically low on memory (0.4 GB free), and it was not restarted. There were no request errors and no unparseable outputs in the 118.
- **Speed:** mean **9.0 s/alert** (bootstrap 95% CI 7.8–10.2), median 5.9 s, 95th percentile 22.6 s, maximum 40.8 s. Prompts average 1,002 tokens (median 740, maximum 3,119, all within the context window). Prompt processing ran at only about 100 tokens/s, which is slow for this GPU; the machine was nearly out of RAM, so the figure may be pessimistic.
- **Projection (upper end of the CI):** A1 on two local models (4,471 alerts each) 25 h; the reduced A2 (the two SOCBED datasets, two models) 2 h; the worst case (all 8,322 alerts on two models, plus the reduced A2) 49 h.
- **Criterion 4 fires only if even the reduced plan exceeds about 72 h. It does not.**

## Findings that shape the brief

1. **Zero-shot Qwen3-4B was degenerate on this task.** It answered "Attack" for all 118 alerts (68 TP, 50 FP, 0 TN, 0 FN; FPR 1.0). On a balanced sample, predicting one class scores F1 0.67 (precision 0.5, recall 1.0), so F1 alone would flatter it. A1 needs to report TPR and FPR (or AUROC from a confidence score), not F1 alone. This is a risk for the "small local models" arm of the plan; it is consistent with the benchmark's own weak models (Llama 3.1 8B: FPR 0.80).
2. **The LLMs in the benchmark see the rule name.** The prompt contains `rule_name`, `attack_type` and `kill_chain_all`. A rule-majority lookup is therefore not a different information source; it measures how much of the label the LLM could get from that field alone. An arm with those fields hidden would separate the two.
3. **Rule lookup cannot generalise to unseen rules.** Under 5-fold cross-validation grouped by rule, the baseline predicts Non-Attack for every held-out rule (TPR 0, FPR 0). A1's grouped-split analysis therefore needs a baseline that uses the alert content (for example TF-IDF with logistic regression); that was not built in this pilot.
4. **The comparison is not like-for-like in supervision.** The baseline is trained on the labels; the LLMs are zero-shot. Near-duplicate alerts (same content with different ports or timestamps) may remain in training; only exact content-duplicates were excluded.

## Takeaways (our interpretation)

- The gap stands and is stronger than the gap scan's number: like-for-like, a lookup that knows only the rule name beats the average LLM by about 0.19 F1 and by 0.41 in FPR.
- The paper must be careful about the claim. "A supervised rule lookup beats zero-shot LLMs" is expected; the contribution is that the benchmark never reported it, how much of the LLMs' errors are the mixed-rule alerts, and what the LLMs do when the rule name is hidden or the rule is unseen.
- Run A1 on the published predictions first (no model calls), then add local models. Plan on one small local model that actually discriminates; Qwen3-4B needs a calibrated threshold or a score, not a hard label.

## Sources

- SecAlertBench artifact, github.com/Dxsssu/SecAlertBench, commit `42a84889fda912ca432c994924a1ccd4b9df6274` (README, `0x02` dataset, `0x03` RQ1 script, `0x04` RQ1 prediction files). Paper: "SecAlertBench: Evaluating Large Language Models for Tier-1 Alert Triage in Security Operations Centers" (arXiv ID and venue not found; see the prior-work note).
- CATS repository, github.com/962012d09b/cats, commit `628cf48a6f569cafc463f47d512bc626d0ac366a` (`datasets/socbed_suricata.zip`, `datasets/socbed_sigma.zip`). Uetz et al., arXiv:2609.02465.
- llama.cpp release b11509, github.com/ggml-org/llama.cpp. Qwen3-4B-Instruct-2507 GGUF, huggingface.co/unsloth/Qwen3-4B-Instruct-2507-GGUF.
