import json

import pytest

from src.checks import _bench_function
from src.prompts import (SYSTEM_PROMPT, benchmark_system_prompt, check_benchmark_sources, messages, parse_label,
                         user_message)

from .conftest import FIELDS, fake_record


def test_benchmark_sources_and_system_prompt_are_the_pinned_ones():
    assert all(check_benchmark_sources().values())
    assert SYSTEM_PROMPT == benchmark_system_prompt()
    assert SYSTEM_PROMPT.startswith("\n") and SYSTEM_PROMPT.endswith("\n")   # leading/trailing newlines kept


def test_condition_a_equals_the_benchmark_function():
    bench = _bench_function("build_user_content")
    rec = fake_record(1, rule="规则")
    assert user_message(rec, "a") == bench({k: v for k, v in rec.items() if k != "Label"})
    assert "规则" in user_message(rec, "a")                    # ensure_ascii=False


@pytest.mark.parametrize("cond,removed", [("b", {"rule_name"}),
                                          ("c", {"rule_name", "attack_type", "kill_chain_all"})])
def test_b_and_c_are_a_minus_the_listed_keys_in_order(cond, removed):
    rec = fake_record(2)
    got = json.loads(user_message(rec, cond).split("\n", 1)[1])
    assert list(got) == [f for f in FIELDS if f not in removed]
    assert "Label" not in got


def test_messages_are_system_then_user():
    m = messages(fake_record(3), "a")
    assert [x["role"] for x in m] == ["system", "user"] and m[0]["content"] == SYSTEM_PROMPT


@pytest.mark.parametrize("text,want", [("Attack", "Attack"), (" Non-Attack \n", "Non-Attack"),
                                       ("Non-Attack.", "Non-Attack"), ("I think Attack", "Attack"),
                                       ("Attack, not Non-Attack", "Non-Attack"), ("attack", None), ("", None),
                                       (None, None), ("Benign", None)])
def test_parser_matches_benchmark(text, want):
    assert parse_label(text) == want == _bench_function("parse_label")(text)
