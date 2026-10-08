"""Metrics, AUROC and bootstrap intervals (protocol §6, §7, §7.1 steps 9-10).

Labels are the benchmark's strings; a prediction of None is an invalid (unparseable) response.
Weights are per-alert (§1); omitted weights mean every alert counts 1.
"""
from __future__ import annotations

import numpy as np

from .common import SEED_BOOTSTRAP

ATTACK, NON_ATTACK = "Attack", "Non-Attack"
N_BOOT = 2000
INVALID = -1


def encode(y_true, y_pred) -> tuple[np.ndarray, np.ndarray]:
    """y_true -> bool (Attack); y_pred -> int8: 1 Attack, 0 Non-Attack, -1 invalid (None)."""
    t = np.array([_label(y, allow_none=False) for y in y_true], dtype=bool)
    p = np.array([INVALID if y is None else int(_label(y, allow_none=False)) for y in y_pred], dtype=np.int8)
    return t, p


def _label(y, allow_none: bool):
    if y == ATTACK:
        return True
    if y == NON_ATTACK:
        return False
    if y is None and allow_none:
        return None
    raise ValueError(f"not a benchmark label: {y!r}")


def counts(t: np.ndarray, p: np.ndarray, w: np.ndarray | None = None, invalid: str = "failure") -> dict:
    """Weighted confusion counts (§6).

    invalid="failure" (primary): an invalid response is a false negative on an Attack alert and a false
    positive on a Non-Attack alert. invalid="exclude" (sensitivity analysis; the benchmark's convention):
    invalid responses are dropped.
    """
    w = np.ones(len(t)) if w is None else np.asarray(w, dtype=float)
    valid = p != INVALID
    if invalid == "failure":
        keep = np.ones(len(t), dtype=bool)
        pred = np.where(valid, p == 1, ~t)              # an invalid answer is always the wrong label
    elif invalid == "exclude":
        keep, pred = valid, p == 1
    else:
        raise ValueError(invalid)
    return {"TP": float(w[keep & t & pred].sum()), "FP": float(w[keep & ~t & pred].sum()),
            "TN": float(w[keep & ~t & ~pred].sum()), "FN": float(w[keep & t & ~pred].sum()),
            "n": int(keep.sum()), "n_invalid": int((~valid).sum())}


def from_counts(c: dict) -> dict:
    """TPR, FPR, precision, F1 and balanced accuracy (§6). None marks an undefined value."""
    tp, fp, tn, fn = c["TP"], c["FP"], c["TN"], c["FN"]
    tpr = tp / (tp + fn) if tp + fn > 0 else None
    fpr = fp / (fp + tn) if fp + tn > 0 else None
    precision = tp / (tp + fp) if tp + fp > 0 else None
    f1 = 0.0 if tp == 0 else 2 * tp / (2 * tp + fp + fn)
    bal = (tpr + 1 - fpr) / 2 if tpr is not None and fpr is not None else None
    return {"tpr": tpr, "fpr": fpr, "precision": precision, "f1": f1, "balanced_accuracy": bal}


def hard_metrics(y_true, y_pred, weights=None, invalid: str = "failure") -> dict:
    t, p = encode(y_true, y_pred)
    c = counts(t, p, weights, invalid)
    return {**c, **from_counts(c)}


def valid_coverage(y_pred) -> float:
    return sum(y is not None for y in y_pred) / len(y_pred)


def auroc(t: np.ndarray, s: np.ndarray, w: np.ndarray | None = None) -> float | None:
    """Rank-based (Mann-Whitney) AUROC with ties counted half (§6), optionally weighted (§1).

    Weighted form: sum over (Attack i, Non-Attack j) of w_i*w_j*[s_i > s_j or 1/2 if tied], divided by
    (sum of Attack weights)*(sum of Non-Attack weights). None when a class is absent.
    """
    t = np.asarray(t, dtype=bool)
    s = np.asarray(s, dtype=float)
    w = np.ones(len(t)) if w is None else np.asarray(w, dtype=float)
    if np.isnan(s).any():
        raise ValueError("AUROC needs a score for every alert (filter unavailable scores first)")
    wp, wn = w[t].sum(), w[~t].sum()
    if wp == 0 or wn == 0:
        return None
    _, inv = np.unique(s, return_inverse=True)
    pos = np.bincount(inv, weights=np.where(t, w, 0.0))
    neg = np.bincount(inv, weights=np.where(t, 0.0, w))
    neg_below = np.cumsum(neg) - neg
    return float((pos * (neg_below + 0.5 * neg)).sum() / (wp * wn))


def auroc_with_bounds(t, s_or_none, w=None) -> dict:
    """§7.1 steps 9-10: primary AUROC over available scores, coverage, and the R1 worst/best-case bounds."""
    t = np.asarray(t, dtype=bool)
    avail = np.array([v is not None for v in s_or_none], dtype=bool)
    s = np.array([np.nan if v is None else v for v in s_or_none], dtype=float)
    w = np.ones(len(t)) if w is None else np.asarray(w, dtype=float)
    lower = np.where(avail, s, np.where(t, 0.0, 1.0))
    upper = np.where(avail, s, np.where(t, 1.0, 0.0))
    return {"auroc": auroc(t[avail], s[avail], w[avail]), "coverage": float(avail.mean()),
            "n_available": int(avail.sum()), "lower": auroc(t, lower, w), "upper": auroc(t, upper, w)}


# ---- bootstrap (§6) ---------------------------------------------------------------------------------------

def bootstrap_indices(groups, n_boot: int = N_BOOT, seed: int = SEED_BOOTSTRAP) -> np.ndarray:
    """(n_boot, n) alert indices. Each replicate resamples with replacement within each group: the four
    sampling strata on the shared sample, the two classes on a published sample."""
    groups = np.asarray(groups)
    by_group = [np.flatnonzero(groups == g) for g in sorted(set(groups.tolist()))]
    g = np.random.Generator(np.random.PCG64(seed))
    out = np.empty((n_boot, len(groups)), dtype=np.int64)
    for b in range(n_boot):
        out[b] = np.concatenate([ix[g.integers(0, len(ix), len(ix))] for ix in by_group])
    return out


def cluster_bootstrap_indices(rules, rule_types, n_boot: int = N_BOOT, seed: int = SEED_BOOTSTRAP) -> list:
    """Rule-cluster bootstrap (§6, dependence sensitivity): resample rules with replacement within rule type
    (mixed or single) and take all alerts of each resampled rule. Replicates differ in size."""
    rules, rule_types = np.asarray(rules), np.asarray(rule_types)
    alerts_of = {r: np.flatnonzero(rules == r) for r in sorted(set(rules.tolist()))}
    type_of = {}
    for r, rt in zip(rules.tolist(), rule_types.tolist()):
        if type_of.setdefault(r, rt) != rt:
            raise ValueError(f"rule {r!r} has more than one rule type")
    by_type = [sorted(r for r in alerts_of if type_of[r] == rt) for rt in sorted(set(type_of.values()))]
    g = np.random.Generator(np.random.PCG64(seed))
    out = []
    for _ in range(n_boot):
        out.append(np.concatenate([alerts_of[rs[i]] for rs in by_type for i in g.integers(0, len(rs), len(rs))]))
    return out


def percentile_ci(values, alpha: float = 0.05) -> dict:
    v = np.array([np.nan if x is None else x for x in values], dtype=float)
    ok = v[~np.isnan(v)]
    if len(ok) == 0:
        return {"lo": None, "hi": None, "n_undefined": int(len(v))}
    lo, hi = np.percentile(ok, [100 * alpha / 2, 100 * (1 - alpha / 2)])
    return {"lo": float(lo), "hi": float(hi), "n_undefined": int(len(v) - len(ok))}


def paired_bootstrap(stat, systems: list, replicates, n: int, pairs: list[tuple] = ()) -> dict:
    """Point estimates and percentile intervals from the SAME resamples for every system (§6).

    stat(system, idx) -> float or None, evaluated on alert indices idx; the point estimate uses all n alerts.
    Differences are a - b per replicate.
    """
    full_index = np.arange(n)
    draws = {s: [stat(s, idx) for idx in replicates] for s in systems}
    out = {"systems": {s: {"point": stat(s, full_index), **percentile_ci(draws[s])} for s in systems},
           "differences": {}}
    for a, b in pairs:
        pa, pb = stat(a, full_index), stat(b, full_index)
        diffs = [None if x is None or y is None else x - y for x, y in zip(draws[a], draws[b])]
        out["differences"][f"{a} - {b}"] = {"point": None if pa is None or pb is None else pa - pb,
                                            **percentile_ci(diffs)}
    return out
