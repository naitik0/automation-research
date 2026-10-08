# Experiment A1

Implements [`docs/experiment-protocol-a1.md`](../../docs/experiment-protocol-a1.md) (approved 2026-10-09). Status and
next steps: [`docs/HANDOFF.md`](../../docs/HANDOFF.md). Production runs are disabled in code until the dry-run
report is approved.

SecAlertBench has no licence: `data/` is git-ignored and never redistributed. No output file holds alert content.

## Reproduce, in order

All commands run from `experiments/a1` with `.venv/Scripts/python.exe` (Python 3.12.10, `requirements.txt`).

| Step | Command | Needs |
|---|---|---|
| 1. Fetch pinned inputs | `./download.sh` | network |
| 2. Frame token lengths (§1) | `python -m src.server start <model>`, then `python -m src.token_lengths --model <model> --scope frame`; repeat for both local models | llama-server (tokenisation only) |
| 3. Sample manifests and P14 | `python -m src.sample` | step 2 files |
| 4. Sample token lengths (P3) | `python -m src.token_lengths --model <model> --scope samples` | llama-server (tokenisation only) |
| 5. Label tokens (§7.1) | `python -m src.lock --label-tokens <model>` | llama-server (tokenisation only) |
| 6. RQ3 folds (P15) | `python -m src.grouped_cv folds` | — |
| 7. Protocol lock | `python -m src.lock`, then `python -m src.lock --verify` | after every `src/` change |
| 8. Offline checks | `python -m src.checks all` (P1, P2, P2b, P3, P11, P14, P15) and `python -m pytest tests` | — |
| 9. Dry run | `python -m src.run_llm --model <model> --subdir final --max-new-calls 60` (repeat until done), then `python -m src.validate_run --model <model> --subdir final` | approval; server or API key |

`python -m src.run_llm --model <model> --print-config` prints the config hash and run directory without contacting
any server or API.

## Layout

| Path | Contents |
|---|---|
| `src/common.py` | paths, pins, seeds, field order, content key and UID, frame |
| `src/prompts.py` | benchmark prompt and parser (read with `ast`, never executed) |
| `src/tfidf_text.py` | §4.1 TF-IDF input text |
| `src/models.py`, `src/server.py` | model parameters (§3), transport clients, llama-server start/stop |
| `src/score.py` | §7.1 label-probability score |
| `src/sample.py`, `src/token_lengths.py` | §1 manifests, length check, P14 |
| `src/run_llm.py` | checkpointed runner (§8, §9); checks the lock and refuses to mix harnesses in one run directory |
| `src/validate_run.py` | read-only run validation (§9) |
| `src/metrics.py` | §6 metrics, AUROC, R1 bounds, paired and rule-cluster bootstrap |
| `src/references.py` | §4 references: always-Attack, rule identity, TF-IDF + logistic regression. For a published file the test input is each row's own published `record` (D10); unmatched rows are kept and counted |
| `src/grouped_cv.py` | §5 RQ3 folds, P15, held-out TF-IDF |
| `src/lock.py` | `config/protocol.lock.json`: pins, hashes, parameters, label tokens, harness |
| `src/checks.py` | offline dry-run checks; reports in `runs/dryrun/checks/` |
| `manifests/` | samples, token lengths, RQ3 folds (tracked) |
| `config/` | protocol lock and label tokens (tracked) |
| `runs/` | run outputs and server logs (git-ignored) |
