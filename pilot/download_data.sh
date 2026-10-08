#!/usr/bin/env bash
# Download pinned SecAlertBench files (no licence in the repo: research use only, do not redistribute).
set -euo pipefail
SHA=42a84889fda912ca432c994924a1ccd4b9df6274
BASE="https://raw.githubusercontent.com/Dxsssu/SecAlertBench/$SHA"
mkdir -p data/secalertbench/scripts data/secalertbench/rq1
get() { curl -sSfL --get "$BASE/$(python -c "import urllib.parse,sys;print(urllib.parse.quote(sys.argv[1]))" "$1")" -o "$2"; }
get "0x02. Processed SecAlertBench Dataset/secalertbench.json" data/secalertbench/secalertbench.json
get "README.md" data/secalertbench/README.md
get "0x03. Evaluation Scripts/RQ1/run_rq1_api_test_eval.py" data/secalertbench/scripts/run_rq1_api_test_eval.py
get "0x03. Evaluation Scripts/RQ1/stats_rq1_summary_metrics.py" data/secalertbench/scripts/stats_rq1_summary_metrics.py
for m in Foundation-Sec-8B-Instruct SecGPT-14B SecGPT-7B claude-sonnet-4-5-20250929 deepseek-v3.1 gemini-3-flash-preview glm-4.7 gpt-5.1-chat kimi-k2-instruct-0905 llama-3.1-405b-instruct llama-3.1-70b-instruct llama-3.1-8b-instruct qwen3-14b qwen3-235b-a22b-instruct-2507 qwen3-30b-a3b-instruct-2507 qwen3-32b; do
  get "0x04. Evaluation Results/RQ1/$m.json" "data/secalertbench/rq1/$m.json"
done
sha256sum data/secalertbench/secalertbench.json data/secalertbench/rq1/*.json > data/secalertbench/SHA256SUMS.txt || true  # NB: Windows Defender removes rq1/gemini-3-flash-preview.json (exploit payloads); not re-downloaded
