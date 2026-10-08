# Experiment protocol A1

**Status:** approved 2026-10-09; amended 2026-10-09 before production (§4 test inputs, D10; see the change log) · implements A1 of the approved [problem brief](problem-brief.md)
**Rule:** nothing in §1–§10 may change after the production run starts. A change needs a new protocol version and a rerun of the affected cells. No result from the dry run (§11) is used in any reported analysis.

Facts in this document come from the pinned SecAlertBench files (commit `42a8488`), the pilot ([notes/soc-alert-triage-pilot.md](../notes/soc-alert-triage-pilot.md)), the llama.cpp b11509 server README, Groq's documentation (model page, reasoning, OpenAI compatibility and rate-limit pages, read 2026-10-09), and Anthropic's model reference. Items marked **[D#]** are decisions awaiting approval (§12).

## 0. Pinned inputs

| Input | Pin |
|---|---|
| SecAlertBench | github.com/Dxsssu/SecAlertBench @ `42a84889fda9…`; `secalertbench.json` sha256 `33f95305…ea3`; benchmark script `0x03…/RQ1/run_rq1_api_test_eval.py` (source of the prompt) |
| Published predictions | `0x04…/RQ1/*.json`: 15 per-alert files usable. `gemini-3-flash-preview.json` is deleted by Windows Defender; only its in-file summary is used **[D9]** |
| llama.cpp | release `b11509`, `llama-b11509-bin-win-cuda-13.4-x64.zip` sha256 `12e4cf85…e2c`, cudart zip sha256 `738f8c25…668` |
| Qwen3-4B | `unsloth/Qwen3-4B-Instruct-2507-GGUF` @ `a06e946…`, file `Qwen3-4B-Instruct-2507-Q4_K_M.gguf`, sha256 `3605803b…7e6` (Apache-2.0) |
| Llama 3.2 3B | `bartowski/Llama-3.2-3B-Instruct-GGUF` @ `5ab33fa…`, file `Llama-3.2-3B-Instruct-Q4_K_M.gguf`; sha256 recorded at download (Llama 3.2 Community Licence, not gated) **[D8]** |
| gpt-oss-120b | Groq, model `openai/gpt-oss-120b`. Groq serves no dated snapshot, so `system_fingerprint` and the returned `model` are logged on every call |
| Claude Haiku 4.5 | Anthropic Messages API, snapshot `claude-haiku-4-5-20251001`, called through the official `anthropic` Python SDK (version pinned at install) |
| Python stack | Python 3.12.10, numpy 1.26.4, scikit-learn 1.8.0, requests 2.32.3, `anthropic` (pinned at install) |

Every pin, plus the git commit of the harness, is written to `experiments/a1/config/protocol.lock.json`. The runner refuses to start if any file hash differs.

## 1. Shared sample (1,000 alerts) and dry-run sample (40 alerts)

**Unit of analysis: a unique alert.**
- An alert's **content key** is the canonical JSON of all its fields except `Label`, `sip`, `dip` and `xff` (`sort_keys=True`, `ensure_ascii=False`). The IP fields are excluded because the released dataset re-randomised them.
- The **alert UID** is the first 16 hex characters of sha256(content key).
- Rows with the same key are collapsed to the row with the lowest index. Of 8,205 keys, 1 has conflicting labels and is excluded, leaving a frame of **8,204** alerts.

**Rule type.** A rule is **mixed** if both labels occur among its rows in the full 8,322-row dataset (31 rules), and **single** otherwise (210 rules).

**Pre-sampling length check.** Each frame alert's condition-(a) prompt is rendered with both local models' chat templates (§2–§3) and tokenised with the server's `/tokenize` endpoint.
- **Excluded:** alerts whose prompt exceeds 8,176 tokens (an 8,192-token context minus 16 for output) in either tokenizer. They leave the frame for **all** models, so every model sees the same alerts.
- The count is reported. In the pilot the longest prompt was 3,119 tokens, so the expected count is about 0.

**Strata.** The frame splits into four strata: rule type × label.

| Stratum h | Frame N_h | Dry run d_h | Post-dry-run frame N′_h = N_h − d_h | Production n_h | Class-balanced weight w_h = 2·N′_h / N′_c |
|---|---|---|---|---|---|
| mixed × Attack | 906 | 10 | 896 | 250 | 2·896/2,389 = 0.7501 |
| single × Attack | 1,503 | 10 | 1,493 | 250 | 2·1,493/2,389 = 1.2499 |
| mixed × Non-Attack | 2,536 | 10 | 2,526 | 250 | 2·2,526/5,775 = 0.8748 |
| single × Non-Attack | 3,259 | 10 | 3,249 | 250 | 2·3,249/5,775 = 1.1252 |

The table assumes no alert is excluded by the length check. The code recomputes every N_h after that check and never hard-codes the weights.

**Draw.**
1. Sort each stratum by alert UID.
2. Draw the dry-run sample first, without replacement, using `numpy.random.Generator(PCG64(20261010))`.
3. Remove the dry-run alerts from the frame.
4. Draw the production sample from what remains with `PCG64(20261009)`.

Sampling is uniform within each stratum, with no per-rule cap (D1, settled). As a result, one mixed Non-Attack rule (1,402 of 2,536 frame alerts) is expected to supply about 138 of its 250 alerts. Per-rule counts are reported.

**Why over-representing the mixed rules keeps the comparison valid.**
- Mixed rules are 37.6% of Attack alerts and 43.8% of Non-Attack alerts in the population, against 50% in the sample.
- **Within-sample comparisons** (condition vs condition, model vs model, LLM vs reference) use the same alerts in every cell, so the sampling design cancels out.
- **Comparisons with populations** (the published 50/50 random samples, or "what a random alert looks like") use the sampling weights below. Within each class they restore the population mix of mixed and single rules, giving a class-balanced population like the benchmark's.

**Sampling weights (exact).**
- **Design.** Stratified simple random sampling without replacement, in two phases. First, d_h = 10 dry-run alerts are removed from each stratum. Then n_h = 250 production alerts are drawn uniformly from the N′_h = N_h − d_h alerts that remain.
- **Inclusion probability.** A post-dry-run alert in stratum h is in production with probability π_h = n_h / N′_h. Dry-run alerts have probability 0.
- **Target population: the post-dry-run frame** (8,164 alerts if no length exclusions). The weights are defined for this frame because it is the population the production sample actually represents.
- **Link to the original 8,204-alert frame.** The dry-run alerts were themselves a stratified random draw, so the post-dry-run frame is a random subsample of the original frame. The estimates are therefore also unbiased for the original frame, in expectation over the dry-run draw. The two frames differ by 10 alerts per stratum, at most 1.1% of any stratum.
- **Expansion weights** are 1/π_h = N′_h / n_h. For class-balanced reporting, the weights are normalised within each class c so that each class carries equal total weight, as in the benchmark's 50/50 samples: w_h = (N′_h / N′_c) / (n_h / n_c) = 2·N′_h / N′_c, where N′_c is the class's post-dry-run total and n_c = 500. Each class's weights sum to 500.
- **Which metrics use which weights.** TPR, FPR and each class's score distribution (which drives AUROC) depend only on the within-class weights. Precision, F1 and balanced accuracy use the class-balanced totals.
- Every metric is reported three ways: per stratum, unweighted on the sample, and weighted.

**Outputs.** `manifests/shared_sample.jsonl` and `manifests/dryrun_sample.jsonl`, one row per alert: `alert_uid`, `row_index`, `stratum`, `label`, `rule_name`, `weight`. Their sha256 hashes go into the lock file. Alert content is never copied into the manifests; it is re-read from the pinned dataset.

**Call order.** For each model, the alerts are put in one fixed random order (`PCG64(20261011)`). The runner then issues conditions (a), (b) and (c) for an alert consecutively before moving to the next one. This keeps provider-side drift over time from lining up with conditions.

## 2. Prompts for the three information conditions

The benchmark's prompt is reproduced byte-for-byte. Only the listed fields are removed.

- **System message.** The benchmark's `system_prompt` string from the pinned script, copied verbatim, including its leading and trailing newlines. A test extracts the string from the pinned script (via `ast`) and asserts equality.
- **User message.** `"Alert fields (JSON):\n" + json.dumps(fields, ensure_ascii=False, indent=2)`. This is the benchmark's `build_user_content`. `fields` is the dataset row without `Label` and without the fields removed by the condition. All other fields keep the dataset's key order.

| Condition | Fields removed (besides `Label`) |
|---|---|
| (a) full | none |
| (b) no rule name | `rule_name` |
| (c) no label-revealing metadata | `rule_name`, `attack_type`, `kill_chain_all` |

- Nothing is added to the prompt: no note that fields were removed, and no placeholder.
- The IP fields are the dataset's own values. The published predictions used different random IPs, which is irrelevant to the label.
- Non-ASCII text, such as the Chinese rule names and attack types, is kept as is (`ensure_ascii=False`).
- Each call records the sha256 of the system message and of the user message. The text itself is never logged; it is rebuilt from the manifest.

## 3. Model configuration

All four models get the same system message, user message and parser. Only the transport differs.

| | Qwen3-4B (local) | Llama 3.2 3B (local) | gpt-oss-120b (Groq) | Claude Haiku 4.5 (Anthropic) |
|---|---|---|---|---|
| Identifier | GGUF in §0 | GGUF in §0 | `openai/gpt-oss-120b` | `claude-haiku-4-5-20251001` |
| Endpoint | llama-server `/apply-template` then `/completion` **[D6]** | same | `POST /openai/v1/chat/completions` (raw HTTP) | `client.messages.create` (`anthropic` SDK) |
| Temperature | `-1`: greedy, with probabilities from a plain softmax of the logits (llama.cpp README) | `-1` | `0` (Groq converts it to 1e-8) **[D3]** | `0.0` |
| Max output | `n_predict` 16 | 16 | `max_completion_tokens` 1,024, which covers reasoning **[D3]** | `max_tokens` 16 |
| Other | `n_probs` 20, `cache_prompt` false, `seed` 1234 | same | `reasoning_effort` "low" **[D3]**, `include_reasoning` true (reasoning text logged), `seed` 1234 (best-effort, undocumented) | `system` = system message; no `top_p`/`top_k`, no stop sequences, no thinking |
| Probabilities | top-20 at each generated token | same | not supported by Groq | not available |

**Local server.**
- Command: `llama-server -m <gguf> -ngl 99 -c 8192 -np 1 --seed 1234 --no-cache-prompt --jinja --host 127.0.0.1 --port 8089`. One model is loaded at a time, and the build string from `/props` is logged.
- **Fixed chat template:** the rendered prompt must be identical across days. Llama 3.x templates can insert today's date; if the dry run (P4) finds a date, it is pinned through the template variable (`date_string` = "26 Jul 2024") and the rendered prompt is hashed.

**Parsing (all models, identical to the benchmark's `parse_label`).**
1. Strip whitespace. An exact match to `Attack` or `Non-Attack` is that label.
2. Otherwise, if the text contains `Non-Attack`, the label is Non-Attack.
3. Otherwise, if it contains `Attack`, the label is Attack.
4. Otherwise the response is **invalid**.

For gpt-oss, only the final `content` is parsed, never the reasoning. An empty content or `finish_reason == "length"` with no parseable label is invalid.

**Invalid responses.**
- An invalid response is **not** re-asked; the first answer is final.
- **Documented deviation:** the benchmark re-asked up to 10 times until it got a parseable label (`retry_times` in the pinned script). We do not emulate this. Section 6 says how invalid responses enter the metrics.

**Transport retries.**
- **Retried:** connection errors, timeouts, HTTP 408/409/429 and 5xx. Up to 6 attempts, with exponential backoff (2, 4, 8, 16, 32, 60 s ± 10% jitter) or the `retry-after` header when present.
- **Not retried:** HTTP 400/401/403/404. These stop the run.
- A call still failing after 6 attempts is marked `failed`, is not counted as done, and is retried on the next resume.
- For the Anthropic SDK, automatic retries are disabled (`max_retries=0`) so that the harness's own log records every attempt.

**Concurrency.**
- Local models: 1 request at a time.
- API models: up to 4 concurrent requests, throttled to stay under the observed rate limits.
- Groq's free plan (8K tokens a minute, 200K a day) is too small, so the paid Developer plan is required **[D8]**.

## 4. RQ1: reference baselines

**Test sets.**
- Each of the 15 available published prediction files is scored on **all 2,000 of its rows as published**, including the few rows whose content is duplicated within the file. Labels come from each row's `true_label` **[D7]**.
- **Test input for a published file [D10].** The references read each row's own published `record`, the exact alert that the published model was shown, not the matching dataset row. For TF-IDF this means the §4.1 text is built from that record; the rule-identity reference uses that record's `rule_name`. The record differs from the dataset row only in the re-randomised IP fields.
- **Unmatched published rows [D10].** A few rows per file (0–5 in the pinned files) have no dataset row with the same content key. They stay in the test set and are scored like every other row. Their count is recorded per file and reported as a limitation: because they match no frame alert, no exact content duplicate of them can be removed from training.
- The references are also scored on the shared sample (§1), so they can be compared directly with our four models. On the shared sample, TF-IDF + logistic regression is fitted once per information condition, on the fields visible to the LLM under that condition. The published models all saw the full prompt, so they are compared with condition (a) only. The rule-identity reference doesn't depend on the condition; it is reported once as a diagnostic.

**Training sets (out-of-sample).** For each test set, train on the frame alerts (§1, deduplicated) whose content key is **not** in that test set. That is about 6,200 alerts for a published file and 7,204 for the shared sample (dry-run alerts are not test alerts, so they may be used for training). No test alert, and no content duplicate of one, is ever in training. Training text always comes from the pinned dataset rows (§4.1). The exclusion is by exact content key, so it covers every matched test row; for unmatched published rows (above) there is no exact duplicate to exclude.

| Reference | Hard prediction | Score (for AUROC) |
|---|---|---|
| Always-Attack | Attack for every alert | constant: AUROC is 0.5 by definition, reported only as an anchor |
| Rule-identity reference (diagnostic) | the alert's rule's majority label in training; **tie → Attack**; **rule absent from training → Non-Attack** | the rule's share of Attack in training; for an absent rule, the overall training Attack rate (about 0.23). Predicting Attack when the score is ≥ 0.5 reproduces the hard rule |
| TF-IDF + logistic regression | Attack if p ≥ 0.5 | p(Attack) |

**What "out-of-sample" means for each reference.**
- **Always-Attack:** no training; it ignores the data entirely.
- **Rule-identity reference:** an out-of-sample **diagnostic**. Its rule → label table is built only from the training alerts and applied to the test alerts.
- **TF-IDF + logistic regression:** an out-of-sample **supervised baseline**. It is fitted only on the training alerts, never on a test alert or a content duplicate of one.

**TF-IDF + logistic regression, fixed in advance with no tuning:**
- **Text:** the alert fields visible to the LLM under the condition, concatenated as specified in **§4.1**. Not the literal prompt: there are no instructions, no label names and no constant prompt text.
- **Features:** `HashingVectorizer(analyzer="char", ngram_range=(3,5), n_features=2**20, alternate_sign=False, norm=None, lowercase=False)` (the text is already lowercased by the §4.1 builder) followed by `TfidfTransformer(sublinear_tf=True)`. Hashing keeps memory within 8 GB RAM and needs no vocabulary.
- **Model:** `LogisticRegression(C=1.0, penalty="l2", solver="liblinear", class_weight="balanced", max_iter=1000, random_state=0)`.
- **Why class-balanced weights:** training is about 30% Attack and every test set is about 50%. Balanced weights put the 0.5 threshold at the balanced-class operating point.

### 4.1 TF-IDF input text (decided)

**Field order.** The order is fixed: the dataset's own field order, which is identical in all 8,322 records. Fields removed by the condition are skipped.

| # | Field | (a) | (b) | (c) |
|---|---|---|---|---|
| 1 | `attack_type` | ✓ | ✓ | – |
| 2 | `dip` | ✓ | ✓ | ✓ |
| 3 | `host` | ✓ | ✓ | ✓ |
| 4 | `method` | ✓ | ✓ | ✓ |
| 5 | `rule_name` | ✓ | – | – |
| 6 | `rsp_body` | ✓ | ✓ | ✓ |
| 7 | `kill_chain_all` | ✓ | ✓ | – |
| 8 | `proto` | ✓ | ✓ | ✓ |
| 9 | `xff` | ✓ | ✓ | ✓ |
| 10 | `dport` | ✓ | ✓ | ✓ |
| 11 | `rsp_status` | ✓ | ✓ | ✓ |
| 12 | `parameter` | ✓ | ✓ | ✓ |
| 13 | `sip` | ✓ | ✓ | ✓ |
| 14 | `rsp_header` | ✓ | ✓ | ✓ |
| 15 | `uri` | ✓ | ✓ | ✓ |
| 16 | `req_header` | ✓ | ✓ | ✓ |
| 17 | `req_body` | ✓ | ✓ | ✓ |
| 18 | `sport` | ✓ | ✓ | ✓ |

`Label` is never included. The IP fields (`sip`, `dip`, `xff`) are included because the LLM sees them, even though their values are random.

**Building the text, in order.** The builder's output is the exact input to the vectorizer.
1. **Value to string:** strings are kept as they are; integers become base-10 digits (`str(int)`); JSON null becomes the empty string.
2. **Unicode:** NFC normalisation (`unicodedata.normalize("NFC", value)`).
3. **Line endings:** `\r\n`, then any remaining `\r`, become `\n`.
4. **Join:** the visible values are joined in the order above with a single `\n`. Field names are **not** included.
5. **Lowercasing: performed.** The joined text is lowercased once, in the builder, with Python 3.12's `str.lower()`. The vectorizer itself does no case folding (`lowercase=False`).
6. **Nothing else changes:** no URL-decoding, HTML-unescaping, truncation, whitespace stripping, or payload removal.

**Excluded:** the system prompt, the header `"Alert fields (JSON):"`, the JSON syntax, field names, and the candidate label names as prompt text.

**Kept:** words such as "attack" that occur *inside* an alert's own field values. They are alert data, and the dry run reports how many alerts contain them.

**Reported as diagnostics, not contests.** The two supervised references see about 6,200 labelled alerts and the LLMs see none. The paper reports them as measures of how much label information the data carries (brief §Approach 5).

## 5. RQ3: held-out-rule generalisation (grouped five-fold, on the shared sample)

RQ3 measures performance on alerts from **held-out rules**: rules absent from the supervised baseline's training data.
- **Only TF-IDF + logistic regression is trained.** It is trained on four folds and tested on the fifth, whose rules do not occur in those four folds.
- **The LLMs are zero-shot.** They are never trained, tuned or prompted with examples from SecAlertBench. They are simply evaluated on the same held-out-rule test alerts.
- **"Held-out" describes TF-IDF's training data, not anything the LLMs saw.** RQ3 uses only the 1,000-alert shared sample; no other population is used.

1. **Folds.** The 1,000 shared alerts are split with `StratifiedGroupKFold(n_splits=5, shuffle=True, random_state=20261009)`, using `groups = rule_name` and `y = stratum` (the four sampling strata). This spreads the strata across folds as evenly as rule grouping allows.
   - Every rule is in exactly one fold, so no rule appears in both training and held-out data. The code asserts this, and that no content key is shared between training and held-out data.
   - The alert → fold and rule → fold maps are saved to `manifests/rq3_folds.jsonl`.
2. **TF-IDF.** For each fold k and each condition c ∈ {a, b, c}, §4's TF-IDF + logistic regression is fitted **only on the shared-sample alerts of the other four folds** (about 800 alerts), using the condition-c text (§4.1). It is then tested on the fold-k alerts, whose rules are absent from its training folds.
3. **LLMs (zero-shot).** Nothing is trained. Each model's condition-c predictions from §3 are evaluated on the **same** fold-k held-out-rule test alerts. No new calls are made.
4. **Comparison.** For each condition, LLM vs TF-IDF is reported:
   - per fold;
   - pooled over the five held-out folds. Every one of the 1,000 alerts is held out exactly once, so the pooled sets are identical for both systems.

   Metrics are reported unweighted and with the §1 weights. Differences use the paired bootstrap (§6).
5. **Not used:** the rule-identity reference, because every held-out rule is absent from training by construction.

**Properties of this design, stated in the paper:**
- TF-IDF trains on only about 800 alerts here, compared with about 6,200–7,200 in RQ1.
- The dominant rule (about 138 alerts, §1) falls entirely in one fold, so fold sizes are uneven. The dry run reports them (P15).

## 6. Metrics and confidence intervals

- **Positive class:** Attack. Counts may be weighted (§1), with TP, FP, TN and FN as sums of alert weights.
- **TPR (recall):** TP/(TP+FN).
- **FPR:** FP/(FP+TN).
- **Precision:** TP/(TP+FP); reported as "undefined" when TP+FP = 0.
- **F1:** 2TP/(2TP+FP+FN); defined as 0 when TP = 0.
- **Balanced accuracy:** (TPR + 1 − FPR)/2. Used as a threshold summary for models that only give hard labels.
- **AUROC:** the rank-based Mann–Whitney estimate, with ties averaged (§7).
- **Why F1 is never shown alone:** on a 50/50 sample, always-Attack scores F1 0.67 with FPR 1.0 (pilot: Qwen3-4B did exactly this).
- **Invalid responses (decided).**
  - **Primary operational metrics:** every alert counts, and an invalid response counts as a **failure**: a false negative if the alert is an Attack, a false positive if it is Non-Attack. An unparseable triage output can never improve a score.
  - **Valid-response coverage:** valid responses ÷ all calls, reported separately for every model × condition, overall and per stratum.
  - **Sensitivity analysis:** invalid responses are excluded (the benchmark's conditional convention).
  - **Deviation:** the benchmark's re-asking (up to 10 times) is documented as a deviation (§3) and not emulated.
- **Bootstrap (decided):** percentile bootstrap, B = 2,000, seed `20261012`, 95% intervals.
  - **Paired bootstrap for every comparison.** This covers model vs model, condition vs condition, LLM vs reference, and LLM vs TF-IDF in RQ3.
    - Each replicate draws **one** resample of alert indices, with replacement. On the shared sample it resamples within each of the four sampling strata; on a published sample, within each class.
    - Every system in the comparison is evaluated on that same resample, and the interval for the difference is the percentile interval of the per-replicate differences.
    - Single-system intervals use the same replicates.
  - **RQ3:** the five fitted TF-IDF fold models stay fixed, and only held-out alerts are resampled. The interval therefore reflects test-set sampling, not training variability; the paper says so.
  - **Dependence sensitivity analysis:** a paired **rule-cluster bootstrap**. It resamples rules with replacement, within rule type (mixed or single), taking all of a resampled rule's alerts, with the same pairing. It is reported for the RQ2 condition differences and the RQ3 comparisons.
- **No multiplicity correction.** Intervals are read descriptively, not as significance tests.

## 7. AUROC by system

| System | AUROC? | Score |
|---|---|---|
| Qwen3-4B, Llama 3.2 3B | yes | The label-probability score defined in §7.1. Primary AUROC uses only alerts whose score is available, with coverage reported for each model × condition. R1 gives worst-case and best-case bounds for the unavailable scores. |
| gpt-oss-120b | no | Groq does not support logprobs. Report TPR, FPR, precision, F1 and balanced accuracy only. |
| Claude Haiku 4.5 | no | The Messages API returns no logprobs. Same metrics as gpt-oss. |
| 15 published models | no | Hard labels only. |
| Rule-identity reference | yes | The rule's Attack share in training (many ties). |
| TF-IDF + logistic regression | yes | p(Attack), from the model fitted for the matching condition (and fold, in RQ3). |
| Always-Attack | 0.5 by definition | Reported only as an anchor. |

A single-point "AUROC" computed from hard labels is not reported for any model.

### 7.1 Local-model label-probability score (primary AUROC score)

This procedure is applied **identically to Qwen3-4B and Llama 3.2 3B**, each with its own tokenizer, and with the same parameters and thresholds.

1. **Label strings.** A = `Attack` and N = `Non-Attack`: exactly the benchmark's labels, case-sensitive, with no leading space, quotes or punctuation.
2. **Label tokens.** Each label is tokenised as the first text of the assistant turn, so the tokenizer sees exactly the context the model generates in.
   - Call `/tokenize` on the rendered prompt (from `/apply-template`) with the label string appended. The label's tokens are the ones after the prompt's own tokens. This gives A = (a₁…a_m) and N = (n₁…n_l).
   - The prompt's tokens must be unchanged by the appended label. This is asserted; otherwise check P8 fails.
   - The token IDs and token texts for each model are recorded in `protocol.lock.json`.
3. **Divergence position.** k is the first position where A and N differ. We expect k = 1 for both models, because `Non-Attack` starts with `Non`; P8 reports the actual k.
4. **Multi-token labels.** Only the two tokens at position k (a_k and n_k) are compared. Once the model chooses the divergent token, the label is determined, so the tokens after k are not scored.
5. **Probabilities.** The `/completion` call (temperature `-1`, `n_probs` 20; §3) returns `completion_probabilities`. At generated position k, `top_logprobs` lists the 20 largest log-probabilities of a plain softmax over the whole vocabulary (llama.cpp README).
   - p_A = exp(logprob of a_k) and p_N = exp(logprob of n_k), matched by **token ID**, not by text.
   - If k > 1, the tokens the model actually generated at positions 1…k−1 must equal the shared prefix (a₁…a_{k−1}); otherwise the score is unavailable (step 7).
6. **Score.** s = p_A / (p_A + p_N). This is the model's preference for Attack over Non-Attack at the point where the two labels differ, renormalised over the two labels. s lies in [0, 1].
7. **Availability (C2).** The score is **available** only when **both** p_A and p_N are in the top 20 at position k (and, if k > 1, the generated prefix matches). Then s is computed as in step 6.
   - **Only one label present:** the score is **unavailable**. No value is substituted for the absent label.
   - **Both absent:** the score is **unavailable**.
8. **Score availability is separate from hard-label validity.**
   - An **unavailable score** is never treated as an invalid classification response. The hard label is still parsed from the generated text (§3) and enters the hard-label metrics as usual.
   - An **invalid generated response** doesn't make the score unavailable, because the score uses only the probabilities at position k. If both label probabilities are present, the alert still has an available score. In the hard-label metrics the invalid response still counts as a failure (§6).
9. **Primary AUROC and coverage.**
   - **Primary AUROC:** for each local model × information condition, AUROC is computed only over the alerts whose score is available.
   - **Coverage:** score coverage (available ÷ all 1,000 alerts) is reported separately for every local model × condition, overall and per stratum. In RQ3 it is also reported per held-out fold.
10. **Sensitivity analysis (R1): bounds for unavailable scores.** For each local model × condition, AUROC is recomputed over **all** alerts twice, with every unavailable score replaced by a bound. Available scores are unchanged.
    - **Lower bound (worst case):** an unavailable Attack alert gets 0 and an unavailable Non-Attack alert gets 1. Each is ranked as wrongly as possible.
    - **Upper bound (best case):** an unavailable Attack alert gets 1 and an unavailable Non-Attack alert gets 0. Each is ranked as correctly as possible.
    - Ties with available scores of exactly 0 or 1 are counted as half-concordant (the Mann–Whitney convention).
    - The true AUROC over all alerts, if every score had been observable, lies between the two bounds. Both bounds are reported next to the primary AUROC and its coverage.

## 8. Output schema and directory layout

```
experiments/a1/
  README.md                  how to reproduce, in order
  config/protocol.lock.json  every pin and hash (§0), seeds, model parameters, harness commit
  src/                       sample.py, prompts.py, tfidf_text.py, run_llm.py, references.py, grouped_cv.py, metrics.py, validate_run.py
  tests/                     prompt-fidelity, TF-IDF text, parser, metric, fold and resume tests
  manifests/                 shared_sample.jsonl, dryrun_sample.jsonl, rq3_folds.jsonl, token_lengths.jsonl  (tracked)
  data/                      pinned dataset and published predictions  (git-ignored, re-downloaded by script)
  runs/<phase>/<model_key>/  calls.jsonl, attempts.jsonl, run_meta.json, RUNNING.lock   (phase = dryrun | production)
  results/                   metrics tables (CSV), bootstrap draws summary, figures
```

**`calls.jsonl`** has one line per completed call and is append-only:

```json
{"call_id": "sha256(model_key|condition|alert_uid|system_sha|user_sha|params_sha)",
 "phase": "production", "model_key": "qwen3-4b", "model_id": "...", "condition": "b",
 "alert_uid": "…", "row_index": 123, "stratum": "mixed_attack", "true_label": "Attack", "rule_name": "…",
 "system_sha256": "…", "user_sha256": "…", "params": {…},
 "status": "ok|invalid", "raw_text": "…", "parsed_label": "Attack|Non-Attack|null",
 "finish_reason": "…", "usage": {"prompt_tokens": 0, "completion_tokens": 0, "reasoning_tokens": 0},
 "first_token_top_probs": [["Attack", 0.91], ["Non", 0.08]], "score_attack": 0.919,
 "reasoning_text": "… (gpt-oss only)", "provider_meta": {"system_fingerprint": "…", "response_model": "…", "request_id": "…"},
 "latency_s": 7.9, "n_attempts": 1, "completed_at": "ISO-8601", "harness_commit": "…", "config_hash": "…"}
```

- **Every attempt** (including failed ones) is logged in `attempts.jsonl`: `call_id`, attempt number, start time, HTTP status, error, latency.
- **`run_meta.json`** holds the config hash, the server build string, the GPU, and the start and end times.
- **Alert content is never written to outputs.** This avoids redistributing unlicensed data and the Defender deletions.

## 9. Checkpoint and resume

- **Idempotent IDs.** `call_id` is a hash of everything that determines a request. A call is done exactly when its `call_id` appears in `calls.jsonl` with status `ok` or `invalid`.
- **Write before moving on.** Each finished call is appended as one line, then `flush()` and `os.fsync()` run before the next request is sent. A crash loses at most the call in flight, which is then re-sent and counted once.
- **Resume.**
  1. Read `calls.jsonl`. A trailing partial line (crash mid-write) is detected, moved to `calls.jsonl.partial-<timestamp>`, and dropped.
  2. Build the set of done IDs and skip them.
  3. Retry `failed` calls.
  4. If the config hash in `run_meta.json` differs from the current config, refuse to resume.
- **No duplicates.** A duplicate `call_id` while loading is a hard error. `RUNNING.lock` (holding the process ID and host) prevents two runners writing the same file; a stale lock needs a manual `--break-lock`.
- **Validation (`validate_run.py`)** after every session:
  - the done IDs equal the expected IDs (1,000 alerts × 3 conditions for each model in production);
  - no duplicates;
  - every line parses;
  - hashes match the manifest;
  - it prints the counts of `ok`, `invalid` and `failed` calls.
- **API idempotency.** The Anthropic and Groq requests have no server-side idempotency key. A crash after the provider answers but before the line is written can therefore cause one billed re-send. This is bounded by one call per crash and is visible in `attempts.jsonl`.

## 10. Estimated compute and cost

| Cell | Calls | Basis | Estimate |
|---|---|---|---|
| Qwen3-4B, 3 conditions | 3,000 | pilot 9.0 s/alert (95% CI 7.8–10.2) | 7.5 h (8.5 h at CI upper bound) |
| Llama 3.2 3B, 3 conditions | 3,000 | assumed ≤ Qwen3-4B (smaller); measured in dry run | ≤ 7.5 h (8.5 h) |
| gpt-oss-120b, 3 conditions | 3,000 | about 1,300 input tokens, 500 output tokens budgeted (cap 1,024); $0.15 / $0.60 per M | **$1.49** (at most $2.43 if every call hits the cap) |
| Haiku 4.5, 3 conditions | 3,000 | about 1,300 input, at most 16 output; $1 / $5 per M | **$4.14** |
| References, grouped CV, metrics, bootstrap | 0 | CPU | minutes to under 1 h |
| **Production total** | **12,000** | | **about 15–17 h local; about $5.60 API (at most $6.60)** |
| Dry run (§11) | 480 + 80 repeats | 40 alerts × 4 models × 3 conditions, plus 20 repeats per model | about 45 min local; about $0.50 API |

**Notes on the estimates:**
- Conditions (b) and (c) are slightly shorter than (a), so these estimates are conservative.
- The local runs are unattended and fit into 2–3 overnight sessions.
- API wall-clock time depends on account rate limits. Groq's Developer-plan limits aren't published, so the dry run measures them.
- The whole study, including the dry run, stays under about $7.10, well inside the $20–30 budget.

## 11. Dry run (must pass before production)

**Scope:**
- the 40-alert dry-run sample (10 per stratum, disjoint from production) × 4 models × 3 conditions = 480 calls;
- 20 repeated calls per model, to check determinism;
- all offline checks on the full manifests.

Dry-run outputs are kept under `runs/dryrun/` and **never** reused in results.

**Pass criteria.** All must pass; any failure stops the work and is brought to you, with nothing fixed silently.

| # | Check | Pass |
|---|---|---|
| P1 | Sampling reproducibility | Building the manifests twice from scratch gives byte-identical files. Strata counts are exact, no dry-run alert is in production, and no UID repeats. |
| P2b | TF-IDF text | For all 1,040 alerts × 3 conditions, the text equals the §4.1 construction (field order, normalisation, `\n` joins). It contains no constant prompt text (system prompt, header, field names). Reports how many alerts contain "attack" in their own field values. |
| P2 | Prompt fidelity | For all 1,040 alerts, the condition-(a) user message is byte-identical to the benchmark's own `build_user_content` (imported from the pinned script) and the system message equals the pinned string. Parsing (b) and (c) back to JSON gives exactly (a) minus the listed keys, in the same order. |
| P3 | Context fit | Every production prompt, rendered with each local template, is ≤ 8,176 tokens. Exclusions are counted and reported (§1). |
| P4 | Template stability | Rendering the same 40 prompts again (with the date pinned if found) gives identical hashes, and no date or run-varying text appears. |
| P5 | Equivalence of local endpoints | On 20 alerts, `/apply-template` + `/completion` yields the same label as the pilot's `/v1/chat/completions` for Qwen3-4B. |
| P6 | Transport | 0 calls `failed` after retries; every retry is logged. |
| P7 | Validity | The invalid rate for every model × condition is reported. Any cell above 10% stops the run for review; the prompt is never changed to fix it. |
| P8 | Score extraction (§7.1) | For each local model: label token IDs recorded; the prompt-prefix assertion holds; the divergence position k is reported. Score coverage is reported for each model × condition, and coverage below 95% in any cell stops the run for your review. The distribution of generated first tokens is printed. |
| P9 | Determinism | Local models: 20 repeated calls give identical labels and \|Δscore\| < 1e-3. APIs: label agreement on 20 repeats is reported, and anything below 95% is flagged. |
| P10 | Resume | Killing the runner mid-run and restarting it gives exactly the expected call IDs, with no duplicates, and `attempts.jsonl` shows completed calls were not re-sent. |
| P11 | Metric code | Reproduces each published file's in-file summary (TP, FP, TN, FN, F1) exactly. Passes hand-computed confusion-matrix tests. AUROC equals scikit-learn's `roc_auc_score`. |
| P12 | gpt-oss truncation | At most 2% of calls hit `finish_reason == "length"` at 1,024 tokens. Otherwise the cap is raised to 2,048 (pre-approved) and the dry run is repeated. |
| P14 | Sample concentration report (from the manifest, no calls) | Reports the number of unique rules in the 1,000-alert shared sample; the largest rule's alert count and percentage of the sample; and, per stratum, the number of rules and the largest rule's count and percentage. This is informational: you review it to judge whether one rule dominates. |
| P15 | RQ3 folds | Reports per fold: alerts, rules, class counts and stratum counts. Asserts zero rule overlap and zero content-key overlap between training and held-out data in every fold. Flags any held-out fold that lacks one class, since AUROC is undefined there. |
| P13 | Budget projection | Measured time and tokens per call project production to ≤ 20 h local and ≤ $10 API. |

## 12. Decisions

### Settled (2026-10-09)

| # | Decision |
|---|---|
| D1 | 250 alerts per stratum, uniform within strata, **no per-rule cap**, inverse-probability weights for population-level numbers. The dry run reports rule concentration (P14). |
| D2 | Invalid responses are never re-asked. **Primary metrics count them as failures**; valid-response coverage is reported separately; a sensitivity analysis excludes them. The benchmark's re-asking (up to 10 times) is documented as a deviation. |
| D4 | TF-IDF uses the **visible alert fields only**, in the fixed order and normalisation of §4.1, fitted per condition. No literal prompt text is used. |
| D5 | **Paired** bootstrap (same resampled alerts) for every comparison; paired rule-cluster bootstrap as the dependence sensitivity analysis. |
| RQ3 | Run on the shared sample only. Five folds grouped by rule; TF-IDF trained on the other four folds; LLMs scored on the identical held-out alerts. |
| C1 | TF-IDF text is lowercased once in the builder (`str.lower()`); the vectorizer does no case folding (§4.1). |
| C2 | A local-model AUROC score is available only when **both** label probabilities are in the top 20; otherwise it is unavailable, with no substitution. Coverage is reported for each model × condition (§7.1). |
| R1 | AUROC sensitivity: worst-case and best-case bounds that replace every unavailable score (§7.1 step 10). Unavailable scores are separate from invalid hard labels. |
| D10 | RQ1 references read each published row's own `record` (what that published model was shown) as the test input; training uses pinned-dataset rows outside the test set, excluding exact content-key duplicates. Unmatched published rows stay in the test set; their count is recorded and reported as a limitation (§4). |

### Still open

| # | Decision | Recommendation | Alternative |
|---|---|---|---|
| D3 | gpt-oss-120b settings | `temperature 0` (as the benchmark does; Groq uses 1e-8), `reasoning_effort "low"`, cap 1,024 tokens (raised to 2,048 if P12 fails) | Vendor-recommended temperature 0.5–0.7, or `"medium"` effort |
| D6 | Local endpoint | `/apply-template` + `/completion` (the documented way to get probabilities); equivalence checked in P5 | Keep `/v1/chat/completions` and give up AUROC for local models |
| D7 | Published-file test rows (RQ1) | All 2,000 rows as published (reproduces the headline numbers exactly) | Unique content keys only, as in the pilot |
| D8 | Accounts, licences, spend | You set up a Groq Developer (paid) plan and an Anthropic API key, accept the Llama 3.2 Community Licence ("Built with Llama"), and authorise about $7.10 | Run with Haiku as the only API model |
| D9 | The 16th published model (Gemini) | Analyse 15 models per alert; use the 16th only through its published summary | Open the file in a sandbox or VM with a Defender exclusion (your security call) |

After these are settled, the next steps are to implement `experiments/a1/`, run the dry run, and report P1–P15. Production runs only after you see the dry-run report.

## Change log

| Date | Change | Why |
|---|---|---|
| 2026-10-09 | §4: the test input for a published file is the row's own published `record`; unmatched published rows stay in the test set, with their count reported as a limitation. Added D10 to §12. | Under-specified in the approved text. Settled by the user during offline preparation, before production and before any reference result was computed; it changes only the reference baselines, not any LLM input or output. |
