import pytest

from src.tfidf_text import build_text

from .conftest import fake_record


def test_values_only_in_field_order_joined_by_newline_and_lowercased():
    rec = fake_record(1, rule="SQL注入")
    rec["rsp_body"] = "A\r\nB\rC"
    rec["uri"] = "é"                                    # NFD; becomes NFC é
    t = build_text(rec, "a")
    parts = t.split("\n")
    assert parts[0] == "attack_type-1" and "sql注入" in parts and "é" in parts
    assert "a\nb\nc" in t and "\r" not in t
    assert "80" in parts and "" in parts                       # int -> digits, None (xff) -> empty
    assert "label" not in t and "attack" not in t.replace("attack_type-1", "")


@pytest.mark.parametrize("cond,removed", [("a", ()), ("b", ("rule_name",)),
                                          ("c", ("rule_name", "attack_type", "kill_chain_all"))])
def test_condition_removes_exactly_the_listed_fields(cond, removed):
    rec = fake_record(2, rule="rule-zz")
    t = build_text(rec, cond)
    assert ("rule-zz" in t) == ("rule_name" not in removed)
    assert ("kill_chain_all-2" in t) == ("kill_chain_all" not in removed)
    assert ("attack_type-2" in t) == ("attack_type" not in removed)
    assert len(t.split("\n")) == 18 - len(removed)


def test_bool_value_fails_loudly():
    rec = fake_record(3)
    rec["proto"] = True
    with pytest.raises(TypeError):
        build_text(rec, "a")
