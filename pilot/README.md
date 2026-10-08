# Pilot: SOC alert triage feasibility (ticket 08)

Reproduces [notes/soc-alert-triage-pilot.md](../notes/soc-alert-triage-pilot.md). Run everything from the repo root in Git Bash.
Windows 11, Python 3.12.10 (numpy 1.26.4, requests 2.32.3), GTX 1650 4 GB (driver 617.14), 8 GB RAM. Use `python -X utf8 -P`.

| Step | Command | Output |
|---|---|---|
| Get SecAlertBench (commit `42a8488…`) | `pilot/download_data.sh` | `pilot/data/secalertbench/` + `SHA256SUMS.txt` |
| Criteria 1 and 2 (matching, baseline) | `python -X utf8 -P pilot/01_data_and_baseline.py` | `results/01_data_and_baseline.json`, stdout in `results/01_stdout.txt` |
| Get CATS (commit `628cf48…`) | `pilot/download_cats.sh` | `pilot/data/cats/` |
| CATS labels | `python -X utf8 -P pilot/02_cats_load.py` | `results/02_cats_load.json` |
| Get llama.cpp b11509 + Qwen3-4B Q4_K_M | `pilot/download_runtime.sh` | `pilot/tools/` (about 2.9 GB) |
| Start server | `pilot/tools/llama.cpp/llama-server.exe -m pilot/tools/models/Qwen3-4B-Instruct-2507-Q4_K_M.gguf -ngl 99 -c 8192 --port 8089 --host 127.0.0.1` | log in `results/llama_server.log` |
| Criterion 4 timing | `python -X utf8 -P pilot/03_throughput_qwen3_4b.py` | `results/03_throughput_qwen3_4b.jsonl` |
| Summary + projection | `python -X utf8 -P pilot/04_summarise_throughput.py` | `results/04_throughput_summary.json` |

Notes
- `pilot/data/` and `pilot/tools/` are git-ignored. `pilot/results/` (summaries, per-alert timings with labels and rule names only, no alert payloads) is tracked. The SecAlertBench and CATS repos have no licence: research use only, do not redistribute.
- Windows Defender removes `rq1/gemini-3-flash-preview.json` (it contains exploit payloads). Its in-file summary is hard-coded in `01_data_and_baseline.py` (`GEMINI_SUMMARY`) with the provenance in a comment.
- The timing run was stopped at 118 of 200 alerts by the memory-pressure reaper. Rerun only with enough free RAM (close other programs first); the JSONL is rewritten from scratch.
