import json

import pytest

from src import validate_run
from src.common import sha256_file, sha256_text, write_jsonl
from src.prompts import SYSTEM_SHA256, user_message
from src.run_llm import call_id, call_order, params_sha

from .conftest import fake_record

MODEL = "llama-3.2-3b"


@pytest.fixture
def run(tmp_path, monkeypatch):
    data = [fake_record(i, "Attack" if i % 2 else "Non-Attack", f"r{i}") for i in range(3)]
    manifest = [{"uid": f"u{i}", "row_index": i, "stratum": "single_attack" if i % 2 else "single_non_attack",
                 "label": data[i]["Label"], "rule_name": data[i]["rule_name"], "weight": None} for i in range(3)]
    mpath = tmp_path / "manifest.jsonl"
    write_jsonl(mpath, manifest)
    monkeypatch.setitem(validate_run.PHASE_MANIFESTS, "dryrun", mpath)
    rd = tmp_path / "run"
    rd.mkdir()
    lines, attempts = [], []
    for m, cond in call_order(manifest):
        usha = sha256_text(user_message(data[m["row_index"]], cond))
        cid = call_id(MODEL, cond, m["uid"], usha, params_sha(MODEL))
        lines.append({"call_id": cid, "alert_uid": m["uid"], "row_index": m["row_index"], "stratum": m["stratum"],
                      "true_label": m["label"], "rule_name": m["rule_name"], "condition": cond,
                      "user_sha256": usha, "system_sha256": SYSTEM_SHA256, "params_sha256": params_sha(MODEL),
                      "phase": "dryrun", "model_key": MODEL, "config_hash": "cfg", "harness": "h1", "status": "ok"})
        attempts.append({"call_id": cid, "attempt": 1, "status": "ok"})
    (rd / "run_meta.json").write_text(json.dumps({"config_hash": "cfg", "manifest_sha256": sha256_file(mpath),
                                                  "sessions": [{"harness": "h1"}]}))
    return rd, data, lines, attempts


def write(rd, lines, attempts):
    write_jsonl(rd / "calls.jsonl", lines)
    write_jsonl(rd / "attempts.jsonl", attempts)


def test_complete_clean_run_passes(run):
    rd, data, lines, attempts = run
    write(rd, lines, attempts)
    r = validate_run.validate(rd, "dryrun", MODEL, data=data)
    assert r["pass"] and r["done"] == r["expected"] == 9 and r["ok"] == 9 and not r["problems"]


def test_incomplete_run_is_reported_not_passed(run):
    rd, data, lines, attempts = run
    write(rd, lines[:5], attempts[:5])
    r = validate_run.validate(rd, "dryrun", MODEL, data=data)
    assert not r["pass"] and r["missing"] == 4 and not r["problems"]


def test_duplicates_resends_and_field_mismatches_are_problems(run):
    rd, data, lines, attempts = run
    bad = [dict(x) for x in lines] + [dict(lines[0])]
    bad[1]["true_label"] = "Attack" if bad[1]["true_label"] == "Non-Attack" else "Non-Attack"
    write(rd, bad, attempts + [dict(attempts[2])])
    r = validate_run.validate(rd, "dryrun", MODEL, data=data)
    text = " ".join(r["problems"])
    assert "duplicate" in text and "sent more than once" in text and "true_label" in text


def test_validation_never_writes(run):
    rd, data, lines, attempts = run
    write(rd, lines, attempts)
    with open(rd / "calls.jsonl", "a") as f:
        f.write('{"partial')
    before = {p.name: p.read_bytes() for p in rd.iterdir()}
    r = validate_run.validate(rd, "dryrun", MODEL, data=data)
    assert "trailing partial line True" in " ".join(r["problems"])
    assert {p.name: p.read_bytes() for p in rd.iterdir()} == before
