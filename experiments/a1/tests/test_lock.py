from src.common import ROOT, sha256_file
from src.lock import harness_hash, verify
from src.models import MODELS, model_params


def lock_for(files):
    return {"files": files, "harness": {"hash": harness_hash()},
            "models": {k: {"params": model_params(k), "auroc": MODELS[k]["auroc"]} for k in MODELS}}


def test_matching_lock_has_no_problems():
    assert verify(lock_for({"requirements.txt": sha256_file(ROOT / "requirements.txt")})) == []


def test_changed_or_missing_file_is_a_problem():
    problems = verify(lock_for({"requirements.txt": "0" * 64, "nope.txt": "0" * 64}))
    assert any("hash differs: requirements.txt" in p for p in problems)
    assert any("missing: nope.txt" in p for p in problems)


def test_only_filter_limits_the_file_check():
    assert verify(lock_for({"requirements.txt": "0" * 64}), only=["manifests/"]) == []


def test_harness_and_parameter_changes_are_problems():
    lk = lock_for({})
    lk["harness"]["hash"] = "different"
    lk["models"]["llama-3.2-3b"]["params"] = {**lk["models"]["llama-3.2-3b"]["params"], "n_predict": 17}
    problems = verify(lk)
    assert any("harness differs" in p for p in problems)
    assert any("model parameters differ" in p for p in problems)


def test_auroc_flag_change_is_a_problem():
    lk = lock_for({})
    lk["models"]["qwen3-4b"]["auroc"] = True
    assert any("AUROC reporting differs from the lock: qwen3-4b" in p for p in verify(lk))


def test_d11_qwen_is_hard_label_only_and_llama_keeps_auroc():
    assert MODELS["qwen3-4b"]["auroc"] is False and MODELS["llama-3.2-3b"]["auroc"] is True
    assert not MODELS["gpt-oss-120b"]["auroc"] and not MODELS["claude-haiku-4.5"]["auroc"]
    assert all("auroc" not in model_params(k) for k in MODELS)          # not a request parameter
