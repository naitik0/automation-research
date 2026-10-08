#!/usr/bin/env bash
# Fetch every pinned input for experiment A1 (protocol §0) into experiments/a1/data and experiments/a1/tools.
# SecAlertBench has no licence: research use only, never redistributed (data/ is git-ignored).
# Run from experiments/a1:  ./download.sh
set -euo pipefail
cd "$(dirname "$0")"

SAB_SHA=42a84889fda912ca432c994924a1ccd4b9df6274
SAB="https://raw.githubusercontent.com/Dxsssu/SecAlertBench/$SAB_SHA"
LLAMA_TAG=b11509
QWEN_REV=a06e946bb6b655725eafa393f4a9745d460374c9
LLAMA32_REV=5ab33fa94d1d04e903623ae72c95d1696f09f9e8

enc() { python -c "import urllib.parse,sys;print(urllib.parse.quote(sys.argv[1]))" "$1"; }
get_sab() { [ -s "$2" ] || curl -sSfL "$SAB/$(enc "$1")" -o "$2"; }

mkdir -p data/rq1 tools/llama.cpp tools/models

# SecAlertBench dataset and the RQ1 script that defines the benchmark prompt.
get_sab "0x02. Processed SecAlertBench Dataset/secalertbench.json" data/secalertbench.json
get_sab "0x03. Evaluation Scripts/RQ1/run_rq1_api_test_eval.py" data/run_rq1_api_test_eval.py

# Published per-alert predictions. gemini-3-flash-preview.json is not fetched (D9):
# Windows Defender deletes it because the alerts contain real exploit strings.
for m in Foundation-Sec-8B-Instruct SecGPT-14B SecGPT-7B claude-sonnet-4-5-20250929 deepseek-v3.1 glm-4.7 \
         gpt-5.1-chat kimi-k2-instruct-0905 llama-3.1-405b-instruct llama-3.1-70b-instruct llama-3.1-8b-instruct \
         qwen3-14b qwen3-235b-a22b-instruct-2507 qwen3-30b-a3b-instruct-2507 qwen3-32b; do
  get_sab "0x04. Evaluation Results/RQ1/$m.json" "data/rq1/$m.json"
done

# llama.cpp and Qwen3-4B: reuse the pilot's copies when present (hash-checked by src/lock.py), else download.
for z in "llama-$LLAMA_TAG-bin-win-cuda-13.4-x64.zip" "cudart-llama-bin-win-cuda-13.4-x64.zip"; do
  if [ ! -s "tools/$z" ]; then
    if [ -s "../../pilot/tools/$z" ]; then cp "../../pilot/tools/$z" "tools/$z"
    else curl -sSfL "https://github.com/ggml-org/llama.cpp/releases/download/$LLAMA_TAG/$z" -o "tools/$z"; fi
  fi
  python -c "import zipfile,sys;zipfile.ZipFile(sys.argv[1]).extractall(sys.argv[2])" "tools/$z" tools/llama.cpp
done
Q=Qwen3-4B-Instruct-2507-Q4_K_M.gguf
if [ ! -s "tools/models/$Q" ]; then
  if [ -s "../../pilot/tools/models/$Q" ]; then cp "../../pilot/tools/models/$Q" "tools/models/$Q"
  else curl -sSfL "https://huggingface.co/unsloth/Qwen3-4B-Instruct-2507-GGUF/resolve/$QWEN_REV/$Q" -o "tools/models/$Q"; fi
fi
L=Llama-3.2-3B-Instruct-Q4_K_M.gguf
[ -s "tools/models/$L" ] || curl -sSfL "https://huggingface.co/bartowski/Llama-3.2-3B-Instruct-GGUF/resolve/$LLAMA32_REV/$L" -o "tools/models/$L"
echo "done; run: .venv/Scripts/python.exe -m src.lock"
