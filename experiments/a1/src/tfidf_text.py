"""TF-IDF input text (protocol §4.1): visible alert field values only, fixed order, deterministic normalisation."""
from __future__ import annotations

import unicodedata

from .common import CONDITIONS, FIELD_ORDER


def _value_to_string(v) -> str:
    if v is None:
        return ""
    if isinstance(v, bool):  # not present in SecAlertBench; fail loudly rather than guess
        raise TypeError("boolean field value not covered by §4.1")
    if isinstance(v, int):
        return str(v)
    if isinstance(v, str):
        return v
    raise TypeError(f"unexpected field value type {type(v).__name__}")


def build_text(rec: dict, condition: str) -> str:
    removed = set(CONDITIONS[condition])
    parts = []
    for field in FIELD_ORDER:
        if field in removed:
            continue
        s = _value_to_string(rec[field])                       # step 1
        s = unicodedata.normalize("NFC", s)                    # step 2
        s = s.replace("\r\n", "\n").replace("\r", "\n")        # step 3
        parts.append(s)
    return "\n".join(parts).lower()                            # steps 4-5; step 6: nothing else
