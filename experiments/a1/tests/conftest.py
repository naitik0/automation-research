"""Tests run offline: no llama-server, no API. Modules that read the pinned (git-ignored) data are skipped
on a machine without it (run ./download.sh first)."""
from src.common import BENCH_SCRIPT, DATASET

NEEDS_DATA = ["test_prompts.py", "test_resume.py", "test_validate_run.py", "test_lock.py"]
collect_ignore = [] if DATASET.exists() and BENCH_SCRIPT.exists() else NEEDS_DATA

FIELDS = ("attack_type", "dip", "host", "method", "rule_name", "rsp_body", "kill_chain_all", "proto", "xff",
          "dport", "rsp_status", "parameter", "sip", "rsp_header", "uri", "req_header", "req_body", "sport")


def fake_record(i: int, label: str = "Attack", rule: str = "rule-x") -> dict:
    """A synthetic alert in the dataset's field order (no real alert content)."""
    rec = {f: f"{f}-{i}" for f in FIELDS}
    rec.update({"rule_name": rule, "dport": 80, "sport": 40000 + i, "xff": None, "Label": label})
    return rec
