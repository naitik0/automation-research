"""Benchmark-exact prompts for the three information conditions (protocol §2) and the benchmark parser (§3).

The benchmark's system prompt and its `build_user_content` / `parse_label` sources are read from the pinned
script with `ast` (no import, no execution of downloaded code). Our implementations below must match the
benchmark's function sources exactly; `check_benchmark_sources()` asserts that.
"""
from __future__ import annotations

import ast
import json

from .common import BENCH_SCRIPT, CONDITIONS, FIELD_ORDER, sha256_text

# Exact sources of the two benchmark functions we re-implement (pinned commit 42a8488).
BENCH_BUILD_USER_CONTENT_SRC = (
    'def build_user_content(record: dict[str, Any]) -> str:\n'
    '    fields = dict(record)\n'
    '    return "Alert fields (JSON):\\n" + json.dumps(fields, ensure_ascii=False, indent=2)'
)
BENCH_PARSE_LABEL_SRC = (
    'def parse_label(content: str | None) -> str | None:\n'
    '    if content is None:\n'
    '        return None\n'
    '    text = str(content).strip()\n'
    '    if text in VALID_LABELS:\n'
    '        return text\n'
    '    if "Non-Attack" in text:\n'
    '        return "Non-Attack"\n'
    '    if "Attack" in text:\n'
    '        return "Attack"\n'
    '    return None'
)
VALID_LABELS = ("Attack", "Non-Attack")


def _bench_ast():
    src = open(BENCH_SCRIPT, encoding="utf-8").read()
    return src, ast.parse(src)


def benchmark_system_prompt() -> str:
    """The literal `system_prompt` string from the pinned RQ1 script (via ast.literal_eval, not exec)."""
    _, tree = _bench_ast()
    found = [n.value for n in ast.walk(tree)
             if isinstance(n, ast.Assign) and any(getattr(t, "id", None) == "system_prompt" for t in n.targets)]
    if len(found) != 1:
        raise SystemExit(f"expected one system_prompt assignment, found {len(found)}")
    return ast.literal_eval(found[0])


def check_benchmark_sources() -> dict:
    src, tree = _bench_ast()
    got = {n.name: ast.get_source_segment(src, n) for n in ast.walk(tree)
           if isinstance(n, ast.FunctionDef) and n.name in ("build_user_content", "parse_label")}
    labels = [ast.literal_eval(n.value) for n in ast.walk(tree)
              if isinstance(n, ast.Assign) and any(getattr(t, "id", None) == "VALID_LABELS" for t in n.targets)]
    return {
        "build_user_content_identical": got.get("build_user_content") == BENCH_BUILD_USER_CONTENT_SRC,
        "parse_label_identical": got.get("parse_label") == BENCH_PARSE_LABEL_SRC,
        "valid_labels_identical": labels == [VALID_LABELS],
    }


SYSTEM_PROMPT = benchmark_system_prompt()
SYSTEM_SHA256 = sha256_text(SYSTEM_PROMPT)


def visible_fields(rec: dict, condition: str) -> dict:
    """Dataset row without Label and without the condition's removed fields, in dataset key order."""
    removed = set(CONDITIONS[condition])
    return {k: rec[k] for k in FIELD_ORDER if k not in removed}


def build_user_content(record: dict) -> str:
    fields = dict(record)
    return "Alert fields (JSON):\n" + json.dumps(fields, ensure_ascii=False, indent=2)


def user_message(rec: dict, condition: str) -> str:
    return build_user_content(visible_fields(rec, condition))


def messages(rec: dict, condition: str) -> list[dict]:
    return [{"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_message(rec, condition)}]


def parse_label(content: str | None) -> str | None:
    if content is None:
        return None
    text = str(content).strip()
    if text in VALID_LABELS:
        return text
    if "Non-Attack" in text:
        return "Non-Attack"
    if "Attack" in text:
        return "Attack"
    return None
