# Handoff: experiment A1 (frozen 2026-10-09)

**Read this before running anything.** Experiment execution was **frozen by the user** on 2026-10-09, part-way through the dry run.
- No production call has ever been made.
- The dry run is **incomplete** and **not valid**.
- Nothing may run until the user says so.

## Update 2026-10-09: offline preparation done, clean Llama dry run ready (not run)

The user settled **D3** (temperature 0, reasoning effort low, 1,024 tokens), **D6** (`/apply-template` + `/completion`), **D7** (all 2,000 published rows) and **D8** (budget about $7–8). These are recorded in `config/protocol.lock.json`; §12 of the protocol still lists them under "Still open". The user also approved **D10**, now written into the protocol (§4, §12, change log): for RQ1 the references read each published row's own `record` as the test input, training uses pinned-dataset rows outside the test set, and unmatched published rows stay in the test set and are reported as a limitation (37 rows over 15 files, 0–5 per file). API credentials are still unset.

- **Built (commits `21fbe01`, `b00d7c5`):** `src/metrics.py`, `references.py`, `grouped_cv.py`, `validate_run.py`, `lock.py`, `checks.py`; 78 offline tests; `experiments/a1/README.md`; `config/label_tokens.json`; `manifests/rq3_folds.jsonl`; `manifests/token_lengths_samples_qwen3-4b.jsonl`.
- **Runner changes:**
  - It verifies the lock (file hashes, harness, parameters) and the live label tokens before any request.
  - Every refusal happens before its first write.
  - It refuses to resume a run directory written by another harness.

  The old 94-call directory therefore can't be resumed; it is untouched (sha256 checked).
- **Offline checks:** P1, P2, P2b, P3, P11, P14 and P15 pass (`python -m src.checks all`; reports in `runs/dryrun/checks/`). The remaining checks need model calls.
- **Hashes:**
  - harness `171e9e68338cc886`;
  - lock sha256 `c0a878cc…c6c3b3`, generated from the clean commit `b00d7c5`;
  - clean Llama run config hash `0f76c90d…cf63`, the same configuration as the old run under a different harness.
- **Ready, not run:**
  1. `python -m src.server start llama-3.2-3b`
  2. `python -m src.run_llm --model llama-3.2-3b --subdir final --max-new-calls 60`, twice
  3. `python -m src.validate_run --model llama-3.2-3b --subdir final`
  4. `python -m src.server stop`

  This needs the user's explicit approval.
- **Llama label tokens** were imported from the old run's `run_meta.json` (same GGUF and llama.cpp build). The runner re-checks them live and refuses to start if they differ.

## Topic

**Title:** Robustness of LLM security-alert triage evaluation to simple baselines and label-revealing metadata.

**Main research question (approved):** How robust are reported LLM alert-triage results once simple non-LLM baselines and potentially label-revealing alert metadata are controlled for?

- **RQ1:** How do published zero-shot LLM triage results compare with simple non-LLM reference baselines on the same alerts, and how predictive of the label is rule identity on its own?
- **RQ2:** How does LLM triage performance change when potentially label-revealing fields are removed from the prompt?
- **RQ3:** How do LLMs and a content-based supervised baseline perform on alerts from rules unseen in training?
- **RQ4 (secondary, optional):** How do zero-shot LLMs compare with risk-based alerting (RBA) for alert prioritisation?

Source: [`docs/problem-brief.md`](problem-brief.md). Do not modify it.

## Approvals and current phase

| Item | Status | Commit |
|---|---|---|
| Problem brief | approved 2026-10-08 | `382e44c` |
| A1 experiment protocol ([`docs/experiment-protocol-a1.md`](experiment-protocol-a1.md)) | approved 2026-10-09 | `8dc0838` (title-only fix later) |
| Dry-run infrastructure | **partly built** (see below) | this handoff's commit |
| Dry run (P1–P15) | **interrupted and frozen; incomplete** | — |
| Production run (12,000 calls) | **prohibited** | — |

**Current phase:** A1 dry run, frozen.

**Open protocol decisions (§12) not yet confirmed by the user:**
- **D3, gpt-oss-120b settings.** The code uses the recommendation: temperature 0, reasoning effort "low", 1,024-token cap.
- **D6, local endpoint.** The code uses `/apply-template` + `/completion`.
- **D7, published-file test rows.** All 2,000 rows as published.
- **D8, accounts and spend.** API credentials are **not configured**: `ANTHROPIC_API_KEY` and `GROQ_API_KEY` are unset, and the `ant` CLI is not installed.

**D9 (Gemini) is decided:** stay at **15** published per-alert models. `gemini-3-flash-preview.json` is deleted by Windows Defender because it contains real exploit strings. **Never bypass Defender**: no exclusions, no sandbox workarounds, no in-memory downloads of the per-alert content. Use only its published summary metrics.

## Exact partial dry-run state (verified offline, no calls made during verification)

> **Correction:** the user's freeze message said 50 completed calls. The checkpoint on disk shows **94**. The second runner session started before the interruption and completed 44 more calls before it was stopped. The figures below come from the files themselves.

| Field | Value |
|---|---|
| Model | Llama 3.2 3B (`Llama-3.2-3B-Instruct-Q4_K_M.gguf`, bartowski @ `5ab33fa`), llama.cpp `b11509-1167d3f42` |
| Phase / subdir | `dryrun` / `main` |
| Run directory | `experiments/a1/runs/dryrun/llama-3.2-3b/main/` |
| Manifest | `experiments/a1/manifests/dryrun_sample.jsonl`, sha256 `5a01bc40ad2b14258049e633d482f52ca7783bc370433865b32fa7e4cbd41d6b` (matches `run_meta.json`) |
| Config hash | `0f76c90dd23409bf2ff767bac76c47e57d07981232ecf8b4e3f30de68a25cf63` |
| Expected calls for this model | 120 (40 alerts × 3 conditions) |
| Completed calls (`calls.jsonl`) | **94**, all `ok`. They are exactly the first 94 calls in the fixed call order: 32 alerts; condition a: 32, b: 31, c: 31 |
| Attempts (`attempts.jsonl`) | 94, all `ok`; 0 retries, 0 failed, 0 fatal |
| Invalid responses | 0 |
| Interrupted in flight | at most 1 call (number 95). It has no attempt record, so it will be re-sent on resume |
| Remaining | 26 calls |
| Partial or corrupt lines | none; `calls.jsonl` ends with a newline |
| Duplicates | 0 |
| Runner sessions | 2 (`run_meta.json`): started 19:19:20 and 19:27:30 UTC on 2026-10-08 (00:49 and 00:57 IST on 2026-10-09). Last call completed 19:31:12 UTC |
| `RUNNING.lock` | present and **stale**: PID 2176, which is not running. Left in place on purpose |
| Local score availability (§7.1) | 94 of 94 available (Llama's label tokens: `Attack` vs `Non`,`-`,`Attack`; k = 1) |
| Alert content in outputs | none. Records hold labels, rule names, generated text, token IDs and probabilities only |

**Resume safety: yes, with care.**
- `python -m src.run_llm --model llama-3.2-3b --break-lock` would skip the 94 completed call IDs and run only the remaining 26.
- The runner refuses to resume if the config hash changes. That happens if the model parameters, template kwargs, manifest, system prompt or label tokens change.
- The **remaining 26 calls must not be run until the user unfreezes execution.**

**The 94 calls are not a dry run.** The protocol's dry run needs all of the following, and all P1–P15 gates must pass:
- all four models × 40 alerts × 3 conditions (480 calls);
- 20 repeat calls per model;
- the P5 equivalence calls;
- the P10 resume test.

Treat the 94 calls only as checkpoint and debugging material. **They must never enter reported results** (protocol §11).

## Where things are

**In git:**
- `experiments/a1/download.sh` and `requirements.txt`: pinned inputs and dependencies (Python 3.12.10, numpy 1.26.4, scikit-learn 1.8.0, requests 2.32.3, anthropic 1.12.1, pytest 8.4.2).
- `experiments/a1/src/`, built so far:
  - `common.py`: paths, pins, seeds, field order, content key and UID, frame.
  - `prompts.py`: benchmark prompt, read with `ast`; no execution of downloaded code.
  - `tfidf_text.py`: §4.1 builder.
  - `models.py`: model configurations and clients. The Llama template date is pinned to "26 Jul 2024".
  - `server.py`: starts and stops `llama-server`.
  - `score.py`: §7.1 score.
  - `token_lengths.py`: §1 and P3 length checks.
  - `sample.py`: manifests and the P14 report.
  - `run_llm.py`: checkpointed runner. **Production is disabled in code** (`ALLOWED_PHASES` contains only `dryrun`).
- `experiments/a1/manifests/`:
  - `dryrun_sample.jsonl` (40 alerts) and `shared_sample.jsonl` (1,000 alerts, sha256 `4d0b8f12…dbfb9f`);
  - `sample_summary.json`: weights 0.7501 / 1.2499 / 0.8748 / 1.1252; post-dry-run frame 8,164; 0 length exclusions;
  - token-length files.

**Local only (git-ignored; regenerate with `download.sh` on another machine):**
- `experiments/a1/data/`: dataset, benchmark script, 15 published files. No licence, so never commit it.
- `experiments/a1/tools/`: llama.cpp and the GGUF models.
- `experiments/a1/.venv/`.
- `experiments/a1/runs/`: the 94-call checkpoint and the server logs.

## Not built yet

These were never written. The writes were rejected when execution was frozen.
- `src/metrics.py`
- `src/references.py`
- `src/grouped_cv.py` (RQ3 folds and P15)
- `src/validate_run.py`
- `src/lock.py` (`config/protocol.lock.json` has **not** been generated)
- the P1–P15 check and report scripts
- `tests/` (only an empty `__init__.py`)
- `experiments/a1/README.md`

Also not yet done:
- P3 token lengths for **Qwen3-4B** on the samples (Llama's are done; maximum 4,190 tokens).
- The P1 rebuild comparison.

## Observations so far (preliminary; not P-check results)

- **Frame:** 8,322 rows, 8,205 content keys, 1 label-conflicting key excluded, giving 8,204 alerts. Longest condition-(a) prompt: Qwen 5,031 tokens, Llama 4,966. Both are under the 8,176 limit.
- **Shared-sample concentration (P14 data, not yet reviewed):**
  - 134 unique rules (30 mixed, 104 single).
  - Largest rule: `SQL注入攻击(机器学习)`, 136 alerts (13.6% of the sample), 131 of them in mixed × Non-Attack (52.4% of that stratum).
  - Per stratum, rules / largest rule's share: mixed × Attack 25 / 33.6%; mixed × Non-Attack 29 / 52.4%; single × Attack 81 / 17.6%; single × Non-Attack 23 / 35.2%.
- **Llama 3.2 template:** it inserts today's date ("Today Date: 09 Oct 2026"). This is now pinned with `chat_template_kwargs {"date_string": "26 Jul 2024"}`, as the protocol requires.
- **Server temperature:** llama-server echoes `temperature 0.0` in `generation_settings` although the protocol sends `-1`. Decoding is greedy and the log-probabilities are pre-sampling. Record this in the dry-run report.
- **Qwen3-4B score coverage risk:** in one ad-hoc probe (not a dry-run call), Qwen put probability ≈ 1.0 on `Attack` and `Non` was **not** in the top 20. Under C2 that score is unavailable, so Qwen's score coverage (P8) may fall below 95%.
- **Memory:** free RAM was about 0.5 GB during the work, and an earlier pilot run was killed by Claude Code's memory-pressure reaper. Run local inference in foreground chunks of 60 calls or fewer.

## What the next session must inspect first, in order

1. `git log` and this file. Confirm the user has **explicitly unfrozen** execution before any call.
2. The checkpoint: count `calls.jsonl` and `attempts.jsonl` in `experiments/a1/runs/dryrun/llama-3.2-3b/main/` and compare with the table above. Check the stale lock's PID is dead. Read `run_meta.json` (manifest and config hash).
3. Check the manifests' sha256 against this file and `sample_summary.json`.
4. Read protocol §11 (P1–P15) and §12. Ask the user to confirm D3, D6, D7 and D8, and to provide API credentials **through environment variables, never in chat or files**.
5. Write the missing modules and tests, generate `config/protocol.lock.json`, then complete the dry run for all four models and every P check.
6. **Stop after the dry-run report.** Production (12,000 calls) is prohibited until the user reviews and approves the complete dry-run report with all P1–P15 gates reported.

## Gate requirement (protocol §11)

All of P1–P15 must be run and reported:
- P1 sampling reproducibility
- P2 prompt fidelity, and P2b TF-IDF text
- P3 context fit
- P4 template stability
- P5 local-endpoint equivalence
- P6 transport
- P7 validity
- P8 score extraction and coverage
- P9 determinism
- P10 resume
- P11 metric code
- P12 gpt-oss truncation
- P13 budget projection
- P14 sample concentration
- P15 RQ3 folds

Any failure stops the work and goes to the user; nothing is fixed silently. Dry-run outputs never enter reported results.
