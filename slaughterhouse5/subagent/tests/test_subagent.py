"""
Tests for subagent - the L2 SUBAGENT HOST plane (hosted I-13 learner).

Grounded in the baseline: L2 SUBAGENT HOST = 209068 nodes / 18 bits, host
alphabet 66; the frozen I-13 spec sha; the deterministic operant pool.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from subagent import (  # noqa: E402
    HOST_ALPHABET, HOST_ALPHABET_SIZE, L2_ADDR_MAX, L2_BITS, L2_NODES,
    FROZEN_SPEC_SHA, OPERANT_POOL, THE_TWELVE, SubAgent, propose_operant,
    sha256_hex,
)


def test_l2_plane_matches_baseline():
    assert L2_NODES == 209068
    assert L2_BITS == 18
    assert L2_ADDR_MAX == (1 << 18) - 1 == 262143
    assert HOST_ALPHABET_SIZE == 66


def test_frozen_sha():
    assert FROZEN_SPEC_SHA == "64881ebf502b87bb450f1f39b71066013e0c31a7f78dedcae326f6155ddc6bf8"


def test_host_alphabet_size_and_symbols():
    assert len(HOST_ALPHABET) == 66
    # first 25 are the real I-symbols (THE_TWELVE + "I") + 12 candidate operants
    for sym in (THE_TWELVE + ["I"] + [op[0] for op in OPERANT_POOL]):
        assert sym in HOST_ALPHABET


def test_subagent_attests_and_proposes():
    sa = SubAgent.from_content("sa.agent", b"i am a subagent")
    assert sa.learned_i13 == FROZEN_SPEC_SHA
    assert sa.proposes_operant not in THE_TWELVE
    assert sa.attestation.startswith("sa.agent|content:")


def test_subagent_host_address_in_range():
    sa = SubAgent.from_content("sa.agent", b"host me")
    assert 0 <= sa.l2_address <= L2_ADDR_MAX
    assert sa.host_symbol in HOST_ALPHABET
    # deterministic: same content -> same host binding
    sa2 = SubAgent.from_content("sa.agent", b"host me")
    assert sa.l2_address == sa2.l2_address
    assert sa.host_symbol == sa2.host_symbol


def test_explicit_address_used():
    sa = SubAgent.from_content("sa.agent", b"x", l2_address=12345)
    assert sa.l2_address == 12345
    # out-of-range address is rejected
    try:
        SubAgent.from_content("bad", b"y", l2_address=L2_ADDR_MAX + 1)
        assert False
    except ValueError:
        pass


def test_verify_host_ok_and_boundary():
    sa = SubAgent.from_content("sa.agent", b"ok")
    ok, why = sa.verify_host()
    assert ok, why
    # a tampered (non-frozen) spec fails the hosting boundary
    bad = SubAgent.from_content("bad", b"x")
    bad.learned_i13 = "0" * 64
    ok, why = bad.verify_host()
    assert not ok and "frozen" in why


def test_to_i13_host_collapse():
    sa = SubAgent.from_content("sa.agent", b"collapse me")
    pol = sa.to_i13_host()
    a = pol["ATTRIBUTE"]
    assert a["module"] == "subagent"
    assert a["scope"] == "L2 SUBAGENT HOST"
    assert a["l2_address"] == sa.l2_address
    assert a["host_symbol"] == sa.host_symbol
    assert a["learned_i13"] == FROZEN_SPEC_SHA


if __name__ == "__main__":
    import pytest
    raise SystemExit(pytest.main([__file__, "-v"]))
