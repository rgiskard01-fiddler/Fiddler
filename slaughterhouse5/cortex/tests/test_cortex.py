"""
Tests for cortex - the L4 deep-operand plane (governor + sensor).

Grounded in I,Robot/hermes.i13: plane node counts, 13-bit L4 addresses,
the five parameter-free rules, and the real empirical sensor deltas.
"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from cortex import (  # noqa: E402
    L4_ADDR_MAX, L4_BITS, L4_NODES, PLANES, PLANE_ORDER, RULE_REACH,
    SENSE_L1, SENSE_L2, Cortex, CortexBoundary, Operand, build_operand_table,
)

EXPECT = {"FUNCTIONDEF": "RETURN", "IF": "I", "EXPR": "I"}


def test_planes_match_spec():
    assert PLANES["L1"]["nodes"] == 395162 and PLANES["L1"]["bits"] == 19
    assert PLANES["L2"]["nodes"] == 209068 and PLANES["L2"]["bits"] == 18
    assert PLANES["L3"]["nodes"] == 38742 and PLANES["L3"]["bits"] == 16
    assert PLANES["L4"]["nodes"] == 6662 and PLANES["L4"]["bits"] == 13
    assert PLANE_ORDER == ("L1", "L2", "L3", "L4")


def test_l4_address_space():
    assert L4_BITS == 13
    assert L4_ADDR_MAX == (1 << 13) - 1 == 8191
    assert L4_NODES == 6662


def test_resolve_in_range():
    c = Cortex()
    op = c.resolve(0)
    assert isinstance(op, Operand) and op.addr == 0
    op = c.resolve(6661)
    assert op.addr == 6661
    # deterministic stand-in weights are reproducible
    assert c.resolve(0).weight == build_operand_table()[0].weight


def test_resolve_cortex_only_boundary():
    c = Cortex()
    # address exactly at the trained count is void (refused)
    try:
        c.resolve(6662)
        assert False, "void address must be refused"
    except CortexBoundary:
        pass
    # negative is not an operand
    try:
        c.resolve(-1)
        assert False
    except CortexBoundary:
        pass
    assert c.can_reach(100) and not c.can_reach(9000)


def test_veto_rule():
    # matching closer is allowed
    ok, why = Cortex.veto(["FUNCTIONDEF"], "RETURN", EXPECT)
    assert ok and "matches" in why
    # wrong closer is a wall
    ok, why = Cortex.veto(["FUNCTIONDEF"], "I", EXPECT)
    assert not ok and "veto" in why
    # empty stack -> no closer allowed
    ok, _ = Cortex.veto([], "RETURN", EXPECT)
    assert not ok


def test_supply_owed_rule():
    owed = Cortex.supply_owed(["FUNCTIONDEF", "IF"], EXPECT)
    assert owed == ["I", "RETURN"]   # innermost first
    # an opener with no defined closer contributes nothing
    assert Cortex.supply_owed(["NAME"], EXPECT) == []


def test_depth_rule():
    refuse, why = Cortex.refuse_if_paid(["L1", "L2"], "L2")
    assert refuse and "already open" in why
    refuse, _ = Cortex.refuse_if_paid(["L1"], "L3")
    assert not refuse


def test_idempotence_rule():
    assert Cortex.idempotent("I", "I") is True
    assert Cortex.idempotent("I", "J") is False


def test_address_rule():
    assert Cortex.write_address(0) == 0
    assert Cortex.write_address(8192) == 0      # 13-bit mask
    assert Cortex.write_address(6662) == 6662


def test_sensor_feedback():
    s = Cortex().sense()
    assert s["L1"] == list(SENSE_L1)
    assert s["L2"] == list(SENSE_L2)
    assert "65.0" in s["note"] and "15.0" in s["note"]


def test_verify_clean_trace():
    trace = json.load(open(
        os.path.join(os.path.dirname(__file__), "..", "examples", "veto-trace.json"),
        encoding="utf-8"))
    ok, report = Cortex().verify(trace)
    assert ok, report
    assert any("veto ok" in r for r in report)
    assert any("advice" in r for r in report)


def test_verify_veto_wall_violation():
    bad = [
        {"kind": "veto", "open": ["FUNCTIONDEF"], "closer": "I", "expect": EXPECT},
    ]
    ok, report = Cortex().verify(bad)
    assert not ok
    assert any("WALL VIOLATION" in r for r in report)


def test_to_i13_policy_collapse():
    pol = Cortex().to_i13_policy()
    assert pol["ATTRIBUTE"]["module"] == "cortex"
    assert pol["ATTRIBUTE"]["l4_operands"] == 6662
    assert pol["ATTRIBUTE"]["doctrine"] == "a feature is advice, a veto is a wall"
    assert set(pol["ATTRIBUTE"]["rules"]) == set(RULE_REACH.keys())


if __name__ == "__main__":
    import pytest
    raise SystemExit(pytest.main([__file__, "-v"]))
