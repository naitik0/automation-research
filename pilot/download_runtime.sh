#!/usr/bin/env bash
# Portable llama.cpp (CUDA 13.4, Windows x64) + Qwen3-4B-Instruct-2507 Q4_K_M, pinned. Nothing is installed system-wide.
set -euo pipefail
TAG=b11509
HF_SHA=a06e946bb6b655725eafa393f4a9745d460374c9   # unsloth/Qwen3-4B-Instruct-2507-GGUF (apache-2.0)
mkdir -p tools/llama.cpp tools/models
for z in llama-$TAG-bin-win-cuda-13.4-x64.zip cudart-llama-bin-win-cuda-13.4-x64.zip; do
  [ -f tools/$z ] || curl -sSfL "https://github.com/ggml-org/llama.cpp/releases/download/$TAG/$z" -o tools/$z
  python -X utf8 -P -c "import zipfile,sys;zipfile.ZipFile(sys.argv[1]).extractall(sys.argv[2])" tools/$z tools/llama.cpp
done
M=Qwen3-4B-Instruct-2507-Q4_K_M.gguf
[ -f tools/models/$M ] || curl -sSfL "https://huggingface.co/unsloth/Qwen3-4B-Instruct-2507-GGUF/resolve/$HF_SHA/$M" -o tools/models/$M
sha256sum tools/*.zip tools/models/$M > tools/SHA256SUMS.txt
