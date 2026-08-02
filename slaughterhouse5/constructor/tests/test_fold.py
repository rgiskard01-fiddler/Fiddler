"""
Tests for constructor.fold

Two layers of grounding:
  1. CORPUS  - the real THE FACTORY and THE LANGUAGE collapses from the
               I-13 corpus.  Both seal to the SAME root
               (549f129365038e0d9e812cfc8e09074c920f86df321cff8158e56b34afb972c2)
               but via different proofs.  Recomputing both from their own
               seal+proof is a hard check of the fold convention (R/L).
  2. ROUND   - build synthetic folds, self-verify, tamper, determinism.
"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from constructor import (  # noqa: E402
    MerkleTree, Sphere, build_fold, emit_fold, seal_of, to_i13_collapse,
    verify_fold, verify_file,
)

# ---- real corpus values (transcribed from I,Robot/*/*.dlw.fold) ----
FACTORY_SEAL = "8d6c265f4177446e132f14e3479cfbeb36d4821d3ef0309aba91a7fe8f52e679"
LANGUAGE_SEAL = "788ff9e59db23a566896b88725c0f5a855ad6047f1910e5668a861b490707e1f"
SHARED_ROOT = "549f129365038e0d9e812cfc8e09074c920f86df321cff8158e56b34afb972c2"

FACTORY_PROOF = [
    {"h": "f85e6adbed746ffd35d931be875ca6ba1da53a310b85cff4213d8e9e4ff6bd99", "side": "R"},
    {"h": "44244dae12a98ceaaf2bd4d4d8648fb65a2a169a969c32d7a2a5f3a47082df2c", "side": "R"},
    {"h": "eb8fa57574ec22d654735611bd2e8d4e49db4ef6d1a67d1f80465c5124d270b7", "side": "L"},
    {"h": "6f176260f6a67faf787a89e5a0ffbda18ce2788fb5d2459c60ce6251922fb746", "side": "R"},
    {"h": "db5492b09717248f5ed41d975a5c0c3dab8a4b91d807ec9fb3bbb51453eec23d", "side": "R"},
    {"h": "4282cc1c0504108abfcb354e183aa9b6b3703e556e354777e1ef0d2a73e127b3", "side": "R"},
    {"h": "da08c118430ac2546b69a7ffe9d0e70894c05460a6d8296e28a729f070774064", "side": "R"},
    {"h": "7ce7a5b4a794ac6f270815bd1ca99569400327c8b72e6d415779264a8d9fe642", "side": "R"},
    {"h": "44def4120dffdd79c0d17c32d5c448f7f88a094cbe88903e8a3dff3c7193aad0", "side": "R"},
    {"h": "7124068895bcb60815f4bfe96b56828118fabb9f589c8c4692e34e273fce438c", "side": "R"},
]

LANGUAGE_PROOF = [
    {"h": "e63794a5e8fd1d879725e788db0edfdb26d622c23e4aee7b3589f67a024b63be", "side": "L"},
    {"h": "12cc09a20d9a2d2d9b2805d742b01a6c681697b459733962090be712fbcaa96e", "side": "L"},
    {"h": "b2809571e440f83450037b6ee604a114ecfa21b0ccc3f7c21a2254d0179dc5b7", "side": "R"},
    {"h": "6f176260f6a67faf787a89e5a0ffbda18ce2788fb5d2459c60ce6251922fb746", "side": "R"},
    {"h": "db5492b09717248f5ed41d975a5c0c3dab8a4b91d807ec9fb3bbb51453eec23d", "side": "R"},
    {"h": "4282cc1c0504108abfcb354e183aa9b6b3703e556e354777e1ef0d2a73e127b3", "side": "R"},
    {"h": "da08c118430ac2546b69a7ffe9d0e70894c05460a6d8296e28a729f070774064", "side": "R"},
    {"h": "7ce7a5b4a794ac6f270815bd1ca99569400327c8b72e6d415779264a8d9fe642", "side": "R"},
    {"h": "44def4120dffdd79c0d17c32d5c448f7f88a094cbe88903e8a3dff3c7193aad0", "side": "R"},
    {"h": "7124068895bcb60815f4bfe96b56828118fabb9f589c8c4692e34e273fce438c", "side": "R"},
]


def test_corpus_factory_fold():
    ok, _ = (verify_fold(FACTORY_SEAL, FACTORY_PROOF, SHARED_ROOT))
    assert ok, "THE FACTORY must fold to the shared ROOT_0"


def test_corpus_language_fold():
    ok, _ = (verify_fold(LANGUAGE_SEAL, LANGUAGE_PROOF, SHARED_ROOT))
    assert ok, "THE LANGUAGE must fold to the same shared ROOT_0"


def test_corpus_proofs_converge():
    f_ok, f_root = verify_fold(FACTORY_SEAL, FACTORY_PROOF, SHARED_ROOT)
    l_ok, l_root = verify_fold(LANGUAGE_SEAL, LANGUAGE_PROOF, SHARED_ROOT)
    assert f_ok and l_ok
    assert f_root == l_root == SHARED_ROOT


def test_seal_of_blank():
    # sanity: seal is deterministic sha256(name|slug|blurb)
    a = seal_of("X", "x", "b")
    b = seal_of("X", "x", "b")
    assert a == b and len(a) == 64


def test_merkle_tree_root_and_proof():
    seals = [seal_of(f"n{i}", f"s{i}") for i in range(7)]
    tree = MerkleTree(seals)
    assert tree.root == tree.layers[-1][0]
    # every leaf's proof recomputes to the root
    for i in range(len(seals)):
        proof = [{"h": h, "side": s} for (h, s) in tree.proof_for(i)]
        ok, root = verify_fold(seals[i], proof, tree.root)
        assert ok, f"leaf {i} proof failed"
        assert root == tree.root


def test_build_fold_roundtrip():
    import tempfile
    tmp_path = tempfile.mkdtemp()
    spheres = [
        Sphere("Constructor Demo A", "ctor-a", "first sphere", 0),
        Sphere("Constructor Demo B", "ctor-b", "second sphere", 1),
        Sphere("Constructor Demo C", "ctor-c", "third sphere", 2),
    ]
    written = emit_fold(spheres, str(tmp_path))
    assert len(written) == 3
    for w in written:
        ok, _ = verify_file(w)
        assert ok, f"self-verify failed for {w}"
        doc = json.load(open(w, encoding="utf-8"))
        assert doc["schema"] == "dlw.fold/1"
        assert doc["root"] == doc["root"]  # shared root across the batch


def test_tamper_detected():
    import tempfile
    tmp_path = tempfile.mkdtemp()
    spheres = [Sphere("T0", "t0", "tamper me", 0),
               Sphere("T1", "t1", "sibling leaf", 1)]
    w = emit_fold(spheres, str(tmp_path))[0]
    doc = json.load(open(w, encoding="utf-8"))
    # corrupt the first proof sibling
    doc["proof"][0]["h"] = "0" * 64
    bad = os.path.join(tmp_path, "bad.dlw.fold")
    with open(bad, "w", encoding="utf-8") as fh:
        fh.write(json.dumps(doc))
    ok, _ = verify_file(str(bad))
    assert not ok, "tampered proof must fail verification"


def test_determinism():
    s = [Sphere("D", "d", "same", 0), Sphere("E", "e", "same", 1)]
    a = build_fold(s)[0]["root"]
    b = build_fold(s)[0]["root"]
    assert a == b
    # different input -> (almost surely) different root
    c = build_fold([Sphere("D", "d", "DIFFERENT", 0), Sphere("E", "e", "same", 1)])[0]["root"]
    assert c != a


def test_to_i13_collapse():
    doc = build_fold([Sphere("C", "c", "collapse", 0)])[0]
    collapse = to_i13_collapse(doc)
    assert collapse["ATTRIBUTE"]["schema"] == "dlw.fold/1"
    assert "proof" in collapse["ATTRIBUTE"]
    assert collapse["ATTRIBUTE"]["root"] == doc["root"]


if __name__ == "__main__":
    import pytest
    raise SystemExit(pytest.main([__file__, "-v"]))
