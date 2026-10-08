"""Local-model label-probability score (protocol §7.1)."""
from __future__ import annotations

import math

LABEL_A = "Attack"
LABEL_N = "Non-Attack"


def label_tokens(client, prompt: str, template_kwargs=None) -> dict:
    """Tokenise each label as the first text of the assistant turn (§7.1 step 2) and find k (step 3)."""
    base = client.tokenize(prompt)
    out = {"prompt_prefix_unchanged": True}
    for name, label in (("A", LABEL_A), ("N", LABEL_N)):
        toks = client.tokenize(prompt + label, with_pieces=True)
        ids = [t["id"] for t in toks]
        if ids[:len(base)] != base:
            out["prompt_prefix_unchanged"] = False
        out[name] = [t["id"] for t in toks[len(base):]]
        out[name + "_pieces"] = [t["piece"] for t in toks[len(base):]]
    a, n = out["A"], out["N"]
    k = next((i + 1 for i in range(min(len(a), len(n))) if a[i] != n[i]), None)
    out["k"] = k
    return out


def extract_score(completion_probabilities: list, lt: dict) -> dict:
    """§7.1 steps 4-7. Returns {available, s, p_A, p_N, reason}."""
    k = lt["k"]
    a_k, n_k = lt["A"][k - 1], lt["N"][k - 1]
    if len(completion_probabilities) < k:
        return {"available": False, "reason": "fewer than k generated positions"}
    if k > 1 and [p["id"] for p in completion_probabilities[:k - 1]] != lt["A"][:k - 1]:
        return {"available": False, "reason": "generated prefix differs from shared label prefix"}
    top = {t["id"]: t["logprob"] for t in completion_probabilities[k - 1]["top_logprobs"]}
    has_a, has_n = a_k in top, n_k in top
    if not (has_a and has_n):
        reason = "both labels absent from top-20" if not (has_a or has_n) else \
            ("Non-Attack absent from top-20" if has_a else "Attack absent from top-20")
        return {"available": False, "reason": reason,
                "p_A": math.exp(top[a_k]) if has_a else None, "p_N": math.exp(top[n_k]) if has_n else None}
    p_a, p_n = math.exp(top[a_k]), math.exp(top[n_k])
    return {"available": True, "s": p_a / (p_a + p_n), "p_A": p_a, "p_N": p_n, "reason": None}
