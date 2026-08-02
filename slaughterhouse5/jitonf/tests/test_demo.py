"""Tests for the jitonf (IVM-13-S) engine.

Run directly:   python tests/test_demo.py
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from jitonf import run, jit_run, validate_s, compile_s, lex, parse, OP, disasm, assemble

SRC = '''
I x <- 3 ;
I y <- 4 ;
I sum <- x + y ;
def add(I a, I b) {
  -> a + b ;
}
I r <- add(x, y) ;
I m <- 0 ;
if (x < y) {
  m <- 1 ;
} else {
  m <- 2 ;
}
'''


def test_vm():
    r = run(SRC)
    assert r['env']['x'] == 3
    assert r['env']['sum'] == 7
    assert r['env']['r'] == 7
    assert r['env']['m'] == 1, "if/else should pick the true branch (x<y)"
    print("VM ok:", {k: r['env'][k] for k in ('x', 'sum', 'r', 'm')}, "steps", r['steps'])


def test_jit_matches_vm():
    r = run(SRC)
    j = jit_run(SRC)
    for k in ('x', 'sum', 'r', 'm' if False else 'm'):
        pass
    for k in ('x', 'sum', 'r', 'm'):
        assert j['env'][k] == r['env'][k], "jit != vm for %s" % k
    print("JIT ok; vm == jit")


def test_validator_rejects_fault():
    prog = compile_s(parse(lex(SRC)))
    import copy
    bad = copy.deepcopy(prog)
    k0 = next(iter(bad['fns']))
    # splice an extra BIN ('+') into the function body -> unbalanced stack
    bad['fns'][k0]['code'].insert(3, [OP['BIN'], '+'])
    v = validate_s(bad)
    assert not v['ok'], "validator must reject the injected fault"
    print("Validator rejected fault:", v['errors'][0])


def test_assembler_roundtrip():
    prog = compile_s(parse(lex(SRC)))
    text = disasm(prog)
    back = assemble(text)
    assert back['code'] == prog['code']
    for fn in prog['fns']:
        assert back['fns'][fn]['code'] == prog['fns'][fn]['code']
    print("Assembler round-trip IDENTICAL")


if __name__ == '__main__':
    test_vm()
    test_jit_matches_vm()
    test_validator_rejects_fault()
    test_assembler_roundtrip()
    print("\nALL TESTS PASSED")
