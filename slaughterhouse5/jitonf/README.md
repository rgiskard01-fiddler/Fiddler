========================================================================
| jitonf — IVM-13-S runtime (the `jitonf` module of the I-13 program)  |
========================================================================


> Part of the **I-13 program**, within the **Slaughterhouse5** OS.

`jitonf` is the **Just-In-Time-On-The-Fly** engine: it takes I-13 source and
runs it on the **IVM-13-S** (structured, no absolute jumps) virtual machine.
It is a faithful Python port of the reference implementation in
[`I,Robot/machine/i13-two-scopes.html`](https://github.com/rgiskard01-fiddler/Fiddler)
(the thirteen-form language: lexer, parser, compiler, single-linear-pass
validator, assembler/disassembler, structured executor, and JIT).

## The law: `net = binds - k`

The validator is the heart of the machine. Every opcode carries two numbers:

- **`binds` (b)** — stack slots the opcode *produces*
- **`k`** — stack slots the opcode *consumes*

The net change in stack height after an opcode is **`b − k`**. The validator
walks each region **once, linearly, with no execution and no control-flow
graph**, tracking stack height and an open/close label discipline. If height
goes negative, if branch arms disagree on height, or if a label is never
closed, the program is **rejected statically**. That is what makes faults
catchable before any execution.

## Components (per the I-13 spec)

| Piece | In this repo |
|-------|--------------|
| lexer / parser | `jitonf/ivm13s.py` (`lex`, `parse`) |
| IVM-13-S ISA (17 opcodes) | `OPS` / `OP` / `E` tables |
| compiler (tree → structured bytecode) | `compile_s` |
| single-linear-pass validator | `validate_s` / `validate_one` |
| structured executor | `exec_s` |
| assembler / disassembler | `assemble` / `disasm` |
| JIT (bytecode → Python closure) | `jit` |
| L1 dispatcher (plane per statement) | `plane` / `dispatch_all` |

## Usage

```python
from jitonf import run, jit_run

src = '''
I x <- 3 ;
I y <- 4 ;
I sum <- x + y ;
def add(I a, I b) {
  -> a + b ;
}
I r <- add(x, y) ;
'''

# Tree-walk-free structured path: lex -> parse -> compile -> validate -> execute
res = run(src)
print(res['env']['sum'])   # 7
print(res['steps'])        # instruction count

# JIT path: compiles the bytecode to a real Python closure
j = jit_run(src)
print(j['env']['r'])       # 7  (identical to the VM)
```

`run()` raises `ValueError` if the validator rejects the program.

## Example & tests

- `examples/demo.i13` — a small I-13 program (arithmetic, a function, an `if/else`).
- `tests/test_demo.py` — asserts VM == JIT, the `if/else` branch, and that the
  validator **rejects** an injected fault. Run it with `python tests/test_demo.py`.

## Provenance

Human-directed (**David Lee Wise**) + AI-co-authored (**Hermes Agent**, Nous
Research). Crediting the AI is **provenance, not a derivation claim** — the
semantics here are a port of the published I-13 reference machine, not an
independent invention.

========================================================================
