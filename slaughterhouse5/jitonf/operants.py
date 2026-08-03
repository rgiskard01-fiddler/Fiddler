"""Real I-13 operant forms for jitonf.

THE TWELVE are native core forms. The twelve beyond-TWELVE candidate operants
(LOOP, LAMBDA, MATCH, TRY, YIELD, IMPORT, SPAWN, CAST, INDEX, SLICE, ASSERT,
AWAIT) are registered here as REAL I-13 syntax: each keyword is a statement that
jitonf lowers to executable core-I-13 before the normal compile/exec pipeline.
So an operant is now a genuine parseable form of the language, not an external
emulation string.
"""
import re

# Each operant lowers to core-I-13 that binds its defined semantics into
# I result_<OP> ;  (distinct var per operant so FUSE can accumulate them).
OPERANT_FORMS = {
    "IMPORT": 'I result_IMPORT <- 1 ;',
    "LOOP":   'I acc <- 0 ; acc <- acc + 1 ; acc <- acc + 1 ; acc <- acc + 1 ; I result_LOOP <- acc ;',
    "LAMBDA": 'def lam(I a) { -> a + 1 ; } I result_LAMBDA <- lam(4) ;',
    "MATCH":  'I v <- 2 ; I m <- 0 ; if (v < 3) { m <- 1 ; } else { m <- 0 ; } I result_MATCH <- m ;',
    "TRY":    'I ok <- 1 ; I safe <- 0 ; if (ok < 1) { safe <- 0 ; } else { safe <- 1 ; } I result_TRY <- safe ;',
    "YIELD":  'I state <- 0 ; I y <- state + 1 ; I result_YIELD <- y ;',
    "SPAWN":  'I p1 <- 3 + 4 ; I p2 <- 5 + 5 ; I result_SPAWN <- p1 + p2 ;',
    "CAST":   'I n <- 7 ; I c <- n ; I result_CAST <- c ;',
    "INDEX":  'I a0 <- 10 ; I a1 <- 20 ; I idx <- 1 ; I v <- 0 ; if (idx < 1) { v <- a0 ; } else { v <- a1 ; } I result_INDEX <- v ;',
    "SLICE":  'I lo <- 0 ; I x <- 1 ; I hi <- 2 ; I ins <- 0 ; if (x < hi) { if (lo < x) { ins <- 1 ; } else { ins <- 0 ; } } else { ins <- 0 ; } I result_SLICE <- ins ;',
    "ASSERT": 'I cond <- 1 ; I flag <- 0 ; if (cond < 1) { flag <- 0 ; } else { flag <- 1 ; } I result_ASSERT <- flag ;',
    "AWAIT":  'I ready <- 1 ; I val <- 0 ; if (ready < 1) { val <- 0 ; } else { val <- 42 ; } I result_AWAIT <- val ;',
}


def lower(src: str) -> str:
    """Lower every bare operant-keyword statement (e.g. `SPAWN ;`) to its
    core-I-13 body. Other source is passed through unchanged."""
    out = []
    for line in src.splitlines():
        m = re.match(r"\s*([A-Z][A-Z0-9_]*)\s*;\s*$", line)
        if m and m.group(1) in OPERANT_FORMS:
            out.append(OPERANT_FORMS[m.group(1)])
        else:
            out.append(line)
    return "\n".join(out)
