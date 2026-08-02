"""
Tests for f4 - the 4th I-13 collapse.

Grounded: the committed f4-machine.dlw.fold is a genuine collapse built from
the real I-13 corpus components (factory, language, machine, ...). Its root
must recompute from seal + proof under the hex-string fold convention.
"""
import json
import os
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from f4 import (  # noqa: E402
    MerkleTree, Sphere, build_fold, emit_fold, seal_of, verify_file,
    verify_fold,
)

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REAL_FOLD = os.path.join(REPO, "f4-machine.dlw.fold")


def test_real_f4_fold_verifies():
    assert os.path.isfile(REAL_FOLD), "f4-machine.dlw.fold must be generated"
    fold = json.load(open(REAL_FOLD, encoding="utf-8"))
    ok, computed = verify_fold(fold["seal"], fold["proof"], fold["root"])
    assert ok, f"real f4 fold failed: computed {computed} != root {fold['root']}"
    assert verify_file(REAL_FOLD) is True


def test_f4_engine_verifies_real_factory_fold():
    """f4's fold convention must match the canonical corpus folds (proof that
    the hex-string convention is right, cross-checked against f1's factory)."""
    f1fold = os.path.join(os.path.dirname(REPO), "f1", "f1-factory.dlw.fold")
    if not os.path.isfile(f1fold):
        return  # cross-module artifact not present in this checkout
    fold = json.load(open(f1fold, encoding="utf-8"))
    ok, computed = verify_fold(fold["seal"], fold["proof"], fold["root"])
    assert ok, f"f4 engine failed to verify canonical factory fold: {computed} != {fold['root']}"


def test_build_roundtrip_and_verify():
    spheres = [Sphere("T0", "t0", "a", 0), Sphere("T1", "t1", "b", 1),
               Sphere("T2", "t2", "c", 2), Sphere("T3", "t3", "d", 3)]
    folds = build_fold(spheres)
    d = tempfile.mkdtemp()
    path = os.path.join(d, "t2.dlw.fold")
    emit_fold(folds[2], path)
    assert verify_file(path) is True


def test_tamper_detected():
    fold = json.load(open(REAL_FOLD, encoding="utf-8"))
    fold["proof"][0]["h"] = "0" * 64
    d = tempfile.mkdtemp()
    bad = os.path.join(d, "bad.dlw.fold")
    with open(bad, "w", encoding="utf-8") as fh:
        fh.write(json.dumps(fold))
    assert verify_file(bad) is False


def test_determinism():
    spheres = [Sphere("A", "a", "x", 0), Sphere("B", "b", "y", 1)]
    r1 = build_fold(spheres)[0]["root"]
    r2 = build_fold(spheres)[0]["root"]
    assert r1 == r2
    # different input -> different root
    r3 = build_fold([Sphere("A", "a", "x", 0), Sphere("B", "b", "Z", 1)])[0]["root"]
    assert r3 != r1


def test_merkle_tree_root_and_proof():
    seals = [seal_of(f"n{i}", f"s{i}", f"b{i}") for i in range(7)]
    tree = MerkleTree(seals)
    assert len(tree.root) == 64
    for i in range(7):
        ok, computed = verify_fold(seals[i], tree.proof_for(i), tree.root)
        assert ok, f"leaf {i} proof failed"


if __name__ == "__main__":
    import pytest
    raise SystemExit(pytest.main([__file__, "-v"]))
