"""Checkpoint store (protocol §9): resume, partial-line recovery, duplicates, and refusals that write nothing."""
import json

import pytest

from src.run_llm import Store

META = {"harness": "h1", "model": "m"}


def snapshot(d):
    return {p.name: p.read_bytes() for p in sorted(d.iterdir())}


def line(cid):
    return json.dumps({"call_id": cid, "status": "ok"}) + "\n"


def test_fresh_start_writes_meta_and_lock(tmp_path):
    s = Store(tmp_path / "run", "cfg", META, break_lock=False)
    meta = json.loads((tmp_path / "run" / "run_meta.json").read_text())
    assert meta["config_hash"] == "cfg" and len(meta["sessions"]) == 1
    assert s.lock.exists() and s.done == {}
    s.release()
    assert not s.lock.exists()


def test_resume_skips_done_ids_and_recovers_a_partial_line(tmp_path):
    Store(tmp_path, "cfg", META, False).release()
    (tmp_path / "calls.jsonl").write_text(line("c1") + line("c2") + '{"call_id": "c3", "sta', newline="\n")
    s = Store(tmp_path, "cfg", META, False)
    assert set(s.done) == {"c1", "c2"}
    assert (tmp_path / "calls.jsonl").read_text().endswith("\n")
    assert len(list(tmp_path.glob("calls.jsonl.partial-*"))) == 1
    s.release()


def test_duplicate_call_id_is_a_hard_error_and_releases_the_lock(tmp_path):
    Store(tmp_path, "cfg", META, False).release()
    (tmp_path / "calls.jsonl").write_text(line("c1") + line("c1"), newline="\n")
    with pytest.raises(SystemExit, match="duplicate"):
        Store(tmp_path, "cfg", META, False)
    assert not (tmp_path / "RUNNING.lock").exists()


@pytest.mark.parametrize("cfg,meta,break_lock,match", [
    ("cfg", META, False, "exists"),                               # stale lock, no --break-lock
    ("other", META, True, "config hash differs"),                 # config changed
    ("cfg", {**META, "harness": "h2"}, True, "another harness|refusing to mix"),  # harness changed
])
def test_refusals_leave_the_run_directory_byte_identical(tmp_path, cfg, meta, break_lock, match):
    s = Store(tmp_path, "cfg", META, False)                       # leaves RUNNING.lock behind, like a crash
    (tmp_path / "calls.jsonl").write_text(line("c1"), newline="\n")
    before = snapshot(tmp_path)
    with pytest.raises(SystemExit, match=match):
        Store(tmp_path, cfg, meta, break_lock)
    assert snapshot(tmp_path) == before
    s.release()
