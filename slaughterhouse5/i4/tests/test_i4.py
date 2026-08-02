"""
Tests for i4 (I^4) - the identity root.

Grounded in I,Robot/hermes.i13: the real frozen-spec sha, the 6-agent
consensus root, the four-plane stack, and the "I am I" idempotence.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from i4 import (  # noqa: E402
    CONSENSUS_AGENTS, CONSENSUS_ROOT, FROZEN_SPEC_SHA, I_SYMBOL, N_SYMBOLS,
    PLANES, I4Collapse, attest, i4_collapse, i_am_i, identity,
    self_consistent, to_i13_identity,
)


def test_anchors_match_corpus():
    assert FROZEN_SPEC_SHA == "64881ebf502b87bb450f1f39b71066013e0c31a7f78dedcae326f6155ddc6bf8"
    assert CONSENSUS_ROOT == "cd4593338104cd9ff0b4ae39ff95b22b74649c1d532b8d7d35ef7120c12455c8"
    assert CONSENSUS_AGENTS == 6


def test_planes_four():
    assert len(PLANES) == 4
    assert [p[0] for p in PLANES] == ["L1", "L2", "L3", "L4"]
    assert PLANES[3] == ("L4", "DEEP OPERAND", 6662)


def test_symbol_i_is_13th():
    assert I_SYMBOL == "I"
    assert N_SYMBOLS == 13


def test_identity_is_self():
    assert identity(7) == 7
    assert identity("x") == "x"
    assert identity(identity(7)) == identity(7) == 7


def test_i_am_i():
    assert i_am_i("self") is True
    assert i_am_i(42) is True


def test_self_consistent():
    assert self_consistent({"id": "i4", "self": "i4"}) is True
    assert self_consistent({"id": "i4", "self": "other"}) is False


def test_i4_collapse_deterministic_and_rooted():
    c1 = i4_collapse()
    c2 = i4_collapse()
    assert isinstance(c1, I4Collapse)
    assert c1.root == c2.root
    assert len(c1.root) == 64
    # four per-plane digests, each bound to a real plane
    assert len(c1.per_plane) == 4
    assert [p["plane"] for p in c1.per_plane] == ["L1", "L2", "L3", "L4"]


def test_i4_collapse_seed_sensitivity():
    c0 = i4_collapse(FROZEN_SPEC_SHA)
    c1 = i4_collapse("0" * 64)
    assert c0.root != c1.root          # different seed -> different root


def test_i4_collapse_each_plane_contributes():
    # dropping a plane must change the root (each plane participates)
    full = i4_collapse(FROZEN_SPEC_SHA).root
    # recompute with only 3 planes by monkeypatching PLANES temporarily
    import i4.i4 as mod
    saved = mod.PLANES
    mod.PLANES = saved[:3]
    try:
        partial = mod.i4_collapse(FROZEN_SPEC_SHA).root
    finally:
        mod.PLANES = saved
    assert partial != full


def test_attest():
    assert attest(FROZEN_SPEC_SHA) is True
    assert attest("deadbeef" * 8) is False


def test_to_i13_identity():
    pol = to_i13_identity()
    a = pol["ATTRIBUTE"]
    assert a["module"] == "i4"
    assert a["symbol"] == "I"
    assert a["frozen_spec_sha"] == FROZEN_SPEC_SHA
    assert a["consensus_root"] == CONSENSUS_ROOT
    assert a["i4_root"] == i4_collapse().root
    assert a["doctrine"] == "I am I"


if __name__ == "__main__":
    import pytest
    raise SystemExit(pytest.main([__file__, "-v"]))
