#!/usr/bin/env bash
# Download two small CATS datasets at a pinned commit (repo has no licence: research use only, do not redistribute).
set -euo pipefail
SHA=628cf48a6f569cafc463f47d512bc626d0ac366a
mkdir -p data/cats
for d in socbed_suricata socbed_sigma; do
  curl -sSfL "https://raw.githubusercontent.com/962012d09b/cats/$SHA/datasets/$d.zip" -o data/cats/$d.zip
  mkdir -p data/cats/$d
  python -X utf8 -P -c "import zipfile,sys;zipfile.ZipFile(sys.argv[1]).extractall(sys.argv[2])" data/cats/$d.zip data/cats/$d
done
(cd data/cats && sha256sum *.zip > SHA256SUMS.txt)
