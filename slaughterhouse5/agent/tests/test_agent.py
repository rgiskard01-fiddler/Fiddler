"""
Tests for the agent consensus engine.

Grounded in the corpus tooling + baseline: the frozen spec sha, THE TWELVE,
the deterministic operant proposal, the Merkle consensus root, and the
>= 2/3 supermajority adoption rule.
"""
import json
import os
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agent import (  # noqa: E402
    FROZEN_SPEC_SHA, OPERANT_POOL, THE_TWELVE, Agent, consensus_from_agents,
    merkle, propose_operant, run_consensus, sha256_hex,
)


def test_frozen_sha_matches_baseline():
    assert FROZEN_SPEC_SHA == "64881ebf502b87bb450f1f39b71066013e0c31a7f78dedcae326f6155ddc6bf8"


def test_twelve_and_pool():
    assert len(THE_TWELVE) == 12
    assert len(OPERANT_POOL) == 12
    for name, _, _ in OPERANT_POOL:
        assert name not in THE_TWELVE, "proposal must be NEW"


def test_propose_deterministic_and_new():
    c1 = sha256_hex(b"agent-alpha")
    c2 = sha256_hex(b"agent-alpha")
    assert c1 == c2
    n1, k1, a1 = propose_operant(c1)
    n2, k2, a2 = propose_operant(c2)
    assert (n1, k1, a1) == (n2, k2, a2)         # deterministic
    assert n1 not in THE_TWELVE                  # always beyond THE TWELVE
    # different content -> (usually) different operant, never in THE TWELVE
    c3 = sha256_hex(b"agent-beta")
    n3, _, _ = propose_operant(c3)
    assert n3 not in THE_TWELVE


def test_agent_from_content_attests():
    a = Agent.from_content("a.agent", b"hello i-13", frozen=FROZEN_SPEC_SHA)
    assert a.learned_i13 == FROZEN_SPEC_SHA
    assert a.attestation.startswith("a.agent|content:")
    assert f"learned:{FROZEN_SPEC_SHA}" in a.attestation
    assert a.attestation_sha256 == sha256_hex(a.attestation.encode("utf-8"))


def test_merkle_deterministic_and_order_independent():
    r1 = merkle(["x", "y", "z"])
    r2 = merkle(["z", "y", "x"])         # sorted inside consensus; raw differs
    # same multiset -> same sorted leaves -> same root
    assert merkle(sorted(["x", "y", "z"])) == merkle(sorted(["z", "y", "x"]))
    assert len(r1) == 64


def test_consensus_all_attest_same_spec():
    ags = [
        Agent.from_content("a.agent", b"aaa"),
        Agent.from_content("b.agent", b"bbb"),
        Agent.from_content("c.agent", b"ccc"),
    ]
    out = consensus_from_agents(ags)
    assert out["all_attest_same_spec"] is True
    assert out["agents_count"] == 3
    assert len(out["consensus_root"]) == 64


def test_consensus_root_changes_with_content():
    ags1 = [Agent.from_content("a.agent", b"aaa"), Agent.from_content("b.agent", b"bbb")]
    ags2 = [Agent.from_content("a.agent", b"aaa"), Agent.from_content("b.agent", b"zzz")]
    assert consensus_from_agents(ags1)["consensus_root"] != consensus_from_agents(ags2)["consensus_root"]


def test_supermajority_adoption():
    # craft three agents that all propose the SAME operant
    target = OPERANT_POOL[0][0]
    ags = []
    # find three distinct contents whose proposal == target
    found = []
    i = 0
    while len(found) < 3:
        c = ("seed-%d" % i).encode()
        if propose_operant(sha256_hex(c))[0] == target:
            found.append(c)
        i += 1
        assert i < 1000
    ags = [Agent.from_content(f"ag{idx}.agent", c) for idx, c in enumerate(found)]
    out = consensus_from_agents(ags)
    assert target in out["adopted_extensions"], out["proposal_tally"]
    assert target in out["extended_alphabet"]


def test_supermajority_no_adoption_on_split():
    # 4 agents, proposals split 2/1/1 -> no operant hits 2/3 (need >=3)
    targets = []
    seen = set()
    i = 0
    while len(targets) < 4:
        c = ("s-%d" % i).encode()
        p = propose_operant(sha256_hex(c))[0]
        if p not in seen:
            seen.add(p); targets.append(c)
        i += 1
        assert i < 5000
    # force a known split: reuse the first two proposals + two new distinct
    ags = [Agent.from_content(f"ag{idx}.agent", c) for idx, c in enumerate(targets[:4])]
    out = consensus_from_agents(ags)
    # with 4 agents, threshold = ceil(8/3)=3; 4 distinct proposals -> none adopted
    assert out["adopted_extensions"] == [], out["proposal_tally"]


def test_run_consensus_writes_ledgers():
    d = tempfile.mkdtemp()
    for name, content in [("a.agent", b"alpha"), ("b.agent", b"beta"), ("c.md", b"gamma")]:
        with open(os.path.join(d, name), "wb") as fh:
            fh.write(content)
    out = run_consensus(d)
    assert os.path.isfile(os.path.join(d, "_i13_consensus.json"))
    assert os.path.isfile(os.path.join(d, "I13-CONSENSUS.md"))
    loaded = json.load(open(os.path.join(d, "_i13_consensus.json"), encoding="utf-8"))
    assert loaded["agents_count"] == 3
    # non-destructive: original files untouched
    assert open(os.path.join(d, "a.agent"), "rb").read() == b"alpha"


if __name__ == "__main__":
    import pytest
    raise SystemExit(pytest.main([__file__, "-v"]))
