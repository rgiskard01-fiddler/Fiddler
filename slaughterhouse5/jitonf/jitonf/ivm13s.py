"""
ivm13s.py - faithful Python port of the I-13 reference machine (IVM-13-S).

Source of truth: I,Robot/machine/i13-two-scopes.html  (the thirteen-form
language: lexer, parser, evaluator, the IVM-13-S structured ISA, the
compiler, the single-linear-pass validator, assembler/disassembler, the
structured executor, and the JIT).

The law the validator encodes is:

        net = binds - k

  - "binds" (b) = stack slots an opcode PRODUCES
  - "k"         = stack slots an opcode consumes
  - net height change of an opcode = b - k

No absolute jumps. Validatable in one linear pass per region, with no
execution and no control-flow graph.

Provenance: human-directed (David Lee Wise) + AI-co-authored
(Hermes Agent, Nous Research). Crediting the AI is provenance, not a
derivation claim.
"""

import re

# --------------------------------------------------------------------------
# Tokenizer
# --------------------------------------------------------------------------
_TOKEN_RE = re.compile(r'<-|->|==|!=|<=|>=|[<>+\-*/%().,{};=]|[A-Za-z_]\w*|\d+(?:\.\d)?|"[^"]*"')


def lex(src):
    toks = []
    i = 0
    n = len(src)
    while i < n:
        if src[i].isspace():
            i += 1
            continue
        m = _TOKEN_RE.match(src, i)
        if not m:
            raise SyntaxError('lex @%d %r' % (i, src[i:i + 12]))
        toks.append(m.group(0))
        i = m.end()
    return toks


# --------------------------------------------------------------------------
# Parser  (recursive descent; mirrors parse() in the reference)
# --------------------------------------------------------------------------
def parse(T):
    p = [0]

    def peek():
        return T[p[0]] if p[0] < len(T) else None

    def eat(x):
        if p[0] >= len(T) or T[p[0]] != x:
            raise SyntaxError('want %s got %s' % (x, peek()))
        v = T[p[0]]
        p[0] += 1
        return v

    def is_name(t):
        return bool(t) and re.match(r'^[A-Za-z_]\w*$', t) is not None

    def program():
        b = []
        while p[0] < len(T):
            b.append(stmt())
        return {'t': 'block', 'b': b}

    def block():
        eat('{')
        b = []
        while peek() != '}':
            b.append(stmt())
        eat('}')
        return {'t': 'block', 'b': b}

    def stmt():
        if peek() == 'def':
            p[0] += 1
            name = T[p[0]]; p[0] += 1
            eat('(')
            args = []
            while peek() != ')':
                eat('I')
                args.append(T[p[0]]); p[0] += 1
                if peek() == ',':
                    p[0] += 1
            eat(')')
            return {'t': 'FUNCTIONDEF', 'n': name, 'a': args, 'body': block()}
        if peek() == 'I':
            p[0] += 1
            name = T[p[0]]; p[0] += 1
            if peek() == '<-':
                p[0] += 1
                v = expr()
                if peek() == ';':
                    p[0] += 1
                return {'t': 'ASSIGN', 'n': name, 'v': v, 'decl': 1}
            if peek() == ';':
                p[0] += 1
            return {'t': 'NAME', 'n': name}
        if peek() == 'if':
            p[0] += 1
            c = expr()
            th = block()
            el = None
            if peek() == 'else':
                p[0] += 1
                el = block()
            return {'t': 'IF', 'c': c, 'th': th, 'el': el}
        if peek() == '->':
            p[0] += 1
            v = expr()
            if peek() == ';':
                p[0] += 1
            return {'t': 'RETURN', 'v': v}
        if is_name(peek()) and p[0] + 1 < len(T) and T[p[0] + 1] == '<-':
            name = T[p[0]]; p[0] += 1; p[0] += 1
            v = expr()
            if peek() == ';':
                p[0] += 1
            return {'t': 'ASSIGN', 'n': name, 'v': v}
        e = expr()
        if peek() == ';':
            p[0] += 1
        return {'t': 'EXPR', 'e': 'e'} if False else {'t': 'EXPR', 'e': e}

    def expr():
        return cmp()

    def cmp():
        l = add()
        while peek() in ('<', '>', '<=', '>=', '==', '!='):
            o = T[p[0]]; p[0] += 1
            l = {'t': 'COMPARE', 'o': o, 'l': l, 'r': add()}
        return l

    def add():
        l = mul()
        while True:
            o = peek()
            if o in ('+', '-'):
                p[0] += 1
                l = {'t': 'BINOP', 'o': o, 'l': l, 'r': mul()}
            else:
                return l

    def mul():
        l = post()
        while True:
            o = peek()
            if o in ('*', '/', '%'):
                p[0] += 1
                l = {'t': 'BINOP', 'o': o, 'l': l, 'r': post()}
            else:
                return l

    def post():
        x = prim()
        while True:
            if peek() == '.':
                p[0] += 1
                x = {'t': 'ATTRIBUTE', 'o': x, 'f': T[p[0]]}; p[0] += 1
            elif peek() == '(':
                p[0] += 1
                a = []
                while peek() != ')':
                    a.append(expr())
                    if peek() == ',':
                        p[0] += 1
                eat(')')
                x = {'t': 'CALL', 'f': x, 'a': a}
            else:
                return x

    def prim():
        t = peek()
        if t is None:
            raise SyntaxError('unexpected EOF in prim')
        if re.match(r'^\d', t):
            p[0] += 1
            return {'t': 'CONSTANT', 'v': float(t) if '.' in t else int(t)}
        if t[0] == '"':
            p[0] += 1
            return {'t': 'CONSTANT', 'v': t[1:-1]}
        if t == '(':
            p[0] += 1
            e = expr()
            eat(')')
            return e
        if is_name(t):
            p[0] += 1
            return {'t': 'NAME', 'n': t}
        raise SyntaxError('prim ' + str(t))

    return program()


# --------------------------------------------------------------------------
# IVM-13-S : structured ISA (17 opcodes, no absolute jumps)
# --------------------------------------------------------------------------
OPS = ['CONST', 'ASK', 'ANSWER', 'ATTR', 'ARG', 'BIN', 'CMP', 'BLOCK', 'IF',
       'ELSE', 'END', 'BR_IF', 'CALL', 'RET', 'FUNC', 'DROP', 'HALT']
OP = {n: i for i, n in enumerate(OPS)}

# k = consumed, b = produced.  net height change = b - k  (the law).
E = {
    'CONST':   {'k': 0, 'b': 1},
    'ASK':     {'k': 0, 'b': 1},
    'ANSWER':  {'k': 1, 'b': 0},
    'ATTR':    {'k': 1, 'b': 1},
    'ARG':     {'k': 1, 'b': 0},
    'BIN':     {'k': 2, 'b': 1},
    'CMP':     {'k': 2, 'b': 1},
    'DROP':    {'k': 1, 'b': 0},
    'RET':     {'k': 1, 'b': 1},
    'FUNC':    {'k': 0, 'b': 0},
    'HALT':    {'k': 0, 'b': 0},
    'BLOCK':   {'k': 0, 'b': 0, 'open': 1},
    'IF':      {'k': 1, 'b': 0, 'open': 1},
    'ELSE':    {'k': 0, 'b': 0, 'mid': 1},
    'END':     {'k': 0, 'b': 0, 'close': 1},
    'BR_IF':   {'k': 1, 'b': 0, 'br': 1},
    'CALL':    {'k': None, 'b': 1},
}


def compile_s(ast):
    code = []
    fns = {}
    target = {'cur': code}

    def emit(op, *a):
        target['cur'].append([OP[op], a[0] if a else None])

    def ex(n):
        t = n['t']
        if t == 'CONSTANT':
            emit('CONST', n['v']); return
        if t == 'NAME':
            emit('ASK', n['n']); return
        if t == 'ATTRIBUTE':
            ex(n['o']); emit('ATTR', n['f']); return
        if t == 'BINOP':
            ex(n['l']); ex(n['r']); emit('BIN', n['o']); return
        if t == 'COMPARE':
            ex(n['l']); ex(n['r']); emit('CMP', n['o']); return
        if t == 'CALL':
            for arg in n['a']:
                ex(arg)
            ex(n['f']); emit('CALL', len(n['a'])); return
        raise SyntaxError('ex ' + t)

    def st(n):
        t = n['t']
        if t == 'block':
            for s in n['b']:
                st(s)
            return
        if t == 'ASSIGN':
            ex(n['v']); emit('ANSWER', n['n']); return
        if t == 'NAME':
            return
        if t == 'EXPR':
            ex(n['e']); emit('DROP'); return
        if t == 'RETURN':
            ex(n['v']); emit('RET'); return
        if t == 'IF':
            ex(n['c']); emit('IF')
            st(n['th'])
            if n['el']:
                emit('ELSE'); st(n['el'])
            emit('END'); return
        if t == 'FUNCTIONDEF':
            body = []
            target['cur'] = body
            st(n['body'])
            body.append([OP['CONST'], None])
            body.append([OP['RET'], None])
            target['cur'] = code
            fns[n['n']] = {'params': list(n['a']), 'code': body}
            emit('FUNC', n['n']); return
        raise SyntaxError('st ' + t)

    st(ast)
    code.append([OP['HALT'], None])
    return {'code': code, 'fns': fns}


# --------------------------------------------------------------------------
# Single linear-pass validator.  No execution, no control-flow graph.
# --------------------------------------------------------------------------
def validate_one(code, label):
    h = 0
    ctrl = []
    err = []
    maxh = 0
    unreachable = False
    for i, (op, a) in enumerate(code):
        n = OPS[op]
        e = E.get(n)
        if not e:
            err.append([i, n, 'unknown opcode']); continue
        if e.get('open'):
            if e.get('k'):
                h -= e['k']
                if h < 0:
                    err.append([i, n, 'stack underflow'])
            ctrl.append({'at': i, 'h': h, 'kind': n}); unreachable = False; continue
        if e.get('mid'):
            f = ctrl[-1] if ctrl else None
            if not f:
                err.append([i, n, 'ELSE with no open label']); continue
            if h != f['h'] and not unreachable:
                err.append([i, n, 'branch arms disagree: %s vs %s' % (h, f['h'])])
            h = f['h']; unreachable = False; continue
        if e.get('close'):
            f = ctrl.pop() if ctrl else None
            if not f:
                err.append([i, n, 'END with no open label']); continue
            if h != f['h'] and not unreachable:
                err.append([i, n, 'block leaves %s, entered at %s' % (h, f['h'])])
            h = f['h']; unreachable = False; continue
        if e.get('br'):
            if a >= len(ctrl):
                err.append([i, n, 'br %s exceeds label depth %s' % (a, len(ctrl))])
            h -= e['k']
            if h < 0:
                err.append([i, n, 'stack underflow'])
            continue
        if n == 'CALL':
            k = a or 0
            h += 1 - (k + 1)
        elif n == 'RET':
            h -= 1
            if h < 0:
                err.append([i, n, 'return with empty stack'])
            h += 1
            unreachable = True
        else:
            h += e['b'] - e['k']
        if h < 0:
            err.append([i, n, 'stack underflow, height ' + str(h)])
        maxh = max(maxh, h)
    if ctrl:
        err.append([len(code), 'EOF', str(len(ctrl)) + ' label(s) never closed'])
    return {'ok': len(err) == 0, 'height': h, 'maxh': maxh,
            'errors': err, 'labelsOpen': len(ctrl)}


def validate_s(prog):
    regions = [('<top>', prog['code'])]
    for name, f in prog['fns'].items():
        regions.append(['fn ' + name, f['code']])
    all_errs = []
    maxh = 0
    ok = True
    per = []
    for lab, c in regions:
        r = validate_one(c, lab)
        per.append({'lab': lab, 'n': len(c), 'h': r['height'],
                    'maxh': r['maxh'], 'errs': len(r['errors']), 'ok': r['ok']})
        all_errs.extend(r['errors'])
        maxh = max(maxh, r['maxh'])
        ok = ok and r['ok']
    return {'ok': ok, 'per': per, 'errors': all_errs, 'maxh': maxh}


# --------------------------------------------------------------------------
# Executor for the structured ISA
# --------------------------------------------------------------------------
NIL = {'__nil': 1}


def exec_s(prog, limit=4_000_000):
    globals_ = {'nil': NIL,
                'pair': {'__native': lambda h, t: {'h': h, 't': t}, 'arity': 2}}
    steps = [0]

    def run_region(code, env):
        st = []
        i = 0
        ctrl = []
        while i < len(code):
            steps[0] += 1
            if steps[0] > limit:
                raise RuntimeError('step limit')
            op, a = code[i]
            n = OPS[op]
            if n == 'CONST':
                st.append(a); i += 1
            elif n == 'ASK':
                v = None; e = env
                while e is not None:
                    if a in e['v']:
                        v = e['v'][a]; break
                    e = e['p']
                if e is None:
                    raise NameError('unbound ' + str(a))
                st.append(v); i += 1
            elif n == 'ANSWER':
                env['v'][a] = st.pop(); i += 1
            elif n == 'ATTR':
                st.append(st.pop()[a]); i += 1
            elif n == 'BIN':
                r = st.pop(); l = st.pop()
                if a == '+': st.append(l + r)
                elif a == '-': st.append(l - r)
                elif a == '*': st.append(l * r)
                elif a == '/': st.append(l / r)
                elif a == '%': st.append(l % r)
                else: st.append(None)
                i += 1
            elif n == 'CMP':
                r = st.pop(); l = st.pop()
                if a == '<': st.append(l < r)
                elif a == '>': st.append(l > r)
                elif a == '<=': st.append(l <= r)
                elif a == '>=': st.append(l >= r)
                elif a == '==': st.append(l == r)
                else: st.append(l != r)
                i += 1
            elif n == 'IF':
                c = st.pop()
                if c:
                    ctrl.append({'taken': 1}); i += 1
                else:
                    d = 1; j = i + 1; land = -1
                    while j < len(code):
                        m = OPS[code[j][0]]
                        if m in ('IF', 'BLOCK'):
                            d += 1
                        elif m == 'ELSE' and d == 1:
                            land = j + 1; break
                        elif m == 'END':
                            d -= 1
                            if d == 0:
                                land = j + 1; break
                        j += 1
                    if land < 0:
                        raise RuntimeError('unterminated IF at ' + str(i))
                    if OPS[code[land - 1][0]] == 'ELSE':
                        ctrl.append({'taken': 0})
                    i = land
            elif n == 'ELSE':
                d = 1; j = i + 1; land = -1
                while j < len(code):
                    m = OPS[code[j][0]]
                    if m in ('IF', 'BLOCK'):
                        d += 1
                    elif m == 'END':
                        d -= 1
                        if d == 0:
                            land = j + 1; break
                    j += 1
                if land < 0:
                    raise RuntimeError('unterminated ELSE at ' + str(i))
                if ctrl:
                    ctrl.pop()
                i = land
            elif n == 'END':
                if ctrl:
                    ctrl.pop()
                i += 1
            elif n == 'CALL':
                f = st.pop(); k = a or 0; args = []
                for _q in range(k):
                    args.insert(0, st.pop())
                if f and '__native' in f:
                    st.append(f['__native'](*args)); i += 1; continue
                e2 = {'v': {}, 'p': f['env']}
                for idx, nm in enumerate(f['params']):
                    e2['v'][nm] = args[idx]
                st.append(run_region(f['code'], e2)); i += 1
            elif n == 'RET':
                return st.pop()
            elif n == 'FUNC':
                fn = prog['fns'][a]
                env['v'][a] = {'params': fn['params'], 'code': fn['code'], 'env': env}
                i += 1
            elif n == 'DROP':
                st.pop(); i += 1
            elif n == 'HALT':
                break
            else:
                raise SyntaxError('op ' + n)
        return st[-1] if st else None

    top = {'v': dict(globals_), 'p': None}
    run_region(prog['code'], top)
    return {'env': top, 'steps': steps[0]}


# --------------------------------------------------------------------------
# Assembler + disassembler
# --------------------------------------------------------------------------
def _json(a):
    import json as _j
    return _j.dumps(a)


def disasm(prog):
    out = []

    def region(code, label):
        out.append(label + ':')
        d = 1
        for _i, (op, a) in enumerate(code):
            n = OPS[op]
            if n in ('END', 'ELSE'):
                d -= 1
            out.append('  ' * max(d, 1) + n + ((' ' + _json(a)) if a is not None else ''))
            if n in ('BLOCK', 'IF', 'ELSE'):
                d += 1

    region(prog['code'], '<top>')
    for nm, f in prog['fns'].items():
        region(f['code'], 'fn ' + nm + '(' + ','.join(f['params']) + ')')
    return '\n'.join(out)


def assemble(text):
    import json as _json_mod
    lines = [l.strip() for l in text.split('\n')]
    lines = [l for l in lines if l and not l.startswith('#')]
    prog = {'code': [], 'fns': {}}
    cur = prog['code']
    for l in lines:
        if l.endswith(':'):
            m = re.match(r'^fn\s+(\w+)\(([^)]*)\)', l)
            if m:
                params = [s.strip() for s in m.group(2).split(',') if s.strip()]
                prog['fns'][m.group(1)] = {'params': params, 'code': []}
                cur = prog['fns'][m.group(1)]['code']
            else:
                cur = prog['code']
            continue
        sp = l.find(' ')
        mn = l if sp < 0 else l[:sp]
        arg = None if sp < 0 else _json_mod.loads(l[sp + 1:])
        if OP.get(mn) is None:
            raise SyntaxError('unknown mnemonic ' + mn)
        cur.append([OP[mn], arg])
    return prog


# --------------------------------------------------------------------------
# JIT : bytecode -> Python source -> a real closure
# --------------------------------------------------------------------------
def jit(prog):
    G = {'nil': NIL, 'pair': {'__native': lambda h, t: {'h': h, 'to': t}}}
    F = {}
    for nm in prog['fns']:
        G[nm] = {'__i': nm}

    def gen_body(code):
        lines = ['def _body(L, G, F):', '    st = []']
        indent = ['    ']
        idx = [0]

        def emit(s):
            lines.append(indent[0] + s)

        def walk():
            while idx[0] < len(code):
                op, a = code[idx[0]]
                n = OPS[op]
                idx[0] += 1
                if n == 'CONST':
                    lines.append(indent[0] + 'st.append(%r)' % (a,))
                elif n == 'ASK':
                    emit('st.append(L[%r] if %r in L else G[%r])' % (a, a, a))
                elif n == 'ANSWER':
                    emit('L[%r] = st.pop()' % (a,))
                elif n == 'ATTR':
                    emit('st.append(st.pop()[%r])' % (a,))
                elif n == 'BIN':
                    emit('r = st.pop(); l = st.pop(); st.append(l %s r)' % (a,))
                elif n == 'CMP':
                    m = {'==': '==', '!=': '!=', '<': '<', '>': '>',
                         '<=': '<=', '>=': '>='}[a]
                    emit('r = st.pop(); l = st.pop(); st.append(l %s r)' % (m,))
                elif n == 'CALL':
                    k = a or 0
                    emit('f = st.pop()')
                    emit('A = st[len(st)-%d:]; del st[len(st)-%d:]' % (k, k))
                    emit('st.append(f["__native"](*A) if "__native" in f else F[f["__i"]](*A))')
                elif n == 'RET':
                    emit('return st.pop()')
                elif n == 'DROP':
                    emit('st.pop()')
                elif n == 'IF':
                    emit('if st.pop():')
                    indent[0] = indent[0] + '    '
                    emit('pass')
                    walk()
                elif n == 'BLOCK':
                    indent[0] = indent[0] + '    '
                    emit('pass')
                    walk()
                elif n == 'ELSE':
                    indent[0] = indent[0][:-4]
                    emit('else:')
                    indent[0] = indent[0] + '    '
                    emit('pass')
                    walk()
                elif n == 'END':
                    indent[0] = indent[0][:-4]
                    emit('pass')
                    return
                elif n == 'FUNC':
                    emit('L[%r] = {"__i": %r}' % (a, a))
                elif n == 'HALT':
                    emit('return None')
                else:
                    raise SyntaxError('jit op ' + n)

        walk()
        emit('return st[-1] if st else None')
        return '\n'.join(lines)

    for nm, f in prog['fns'].items():
        src = gen_body(f['code'])
        loc = {}
        exec(src, {'L': {}, 'G': G, 'F': F}, loc)
        _body = loc['_body']
        params = f['params']

        def make(_body, params):
            def call(*args):
                L = {}
                for i, pname in enumerate(params):
                    L[pname] = args[i]
                return _body(L, G, F)
            return call

        F[nm] = make(_body, params)

    src = gen_body(prog['code'])
    loc = {}
    exec(src, {'L': {}, 'G': G, 'F': F}, loc)
    top = loc['_body']

    def run():
        L = dict(G)
        top(L, G, F)
        return L

    return {'run': run, 'F': F, 'src': src}


# --------------------------------------------------------------------------
# L1 dispatcher : plane per statement (measured table)
# --------------------------------------------------------------------------
def plane(kindName, ncall, nargs):
    if ncall == 0:
        return 1
    if ncall == 1 and nargs <= 2:
        return 1
    if ncall <= 2:
        return 2
    if ncall <= 4:
        return 3
    return 4


RULES = {1: 'veto, -I, depth, idem, address',
         2: 'veto, -I, depth',
         3: 'veto, -I, depth',
         4: 'veto, -I, depth',
         5: 'veto, -I, depth'}


def dispatch_all(ast):
    out = []

    def ex(n):
        if not n:
            return [0, 0]
        c = [0]
        a = [0]

        def w(x):
            if not x or not isinstance(x, dict):
                return
            if x.get('t') == 'CALL':
                c[0] += 1
                a[0] += len(x.get('a', []))
            for k, v in x.items():
                if isinstance(v, list):
                    for it in v:
                        w(it)
                elif isinstance(v, dict):
                    w(v)
        w(n)
        return [c[0], a[0]]

    def st(n, d):
        if not n:
            return
        if n['t'] == 'block':
            for k in n['b']:
                st(k, d)
            return
        e = n.get('v') or n.get('e') or n.get('c') or None
        ca = ex(e)
        pl = plane(n['t'], ca[0], ca[1])
        out.append([n['t'], ca[0], ca[1], pl, d])
        for f in ('th', 'el', 'body'):
            if n.get(f):
                st(n[f], d + 1)

    st(ast, 0)
    return out


# --------------------------------------------------------------------------
# Convenience drivers
# --------------------------------------------------------------------------
def run(src, limit=4_000_000):
    toks = lex(src)
    ast = parse(toks)
    prog = compile_s(ast)
    v = validate_s(prog)
    if not v['ok']:
        raise ValueError('I-13 validation rejected: ' + str(v['errors'][:4]))
    res = exec_s(prog, limit=limit)
    return {'env': res['env']['v'], 'steps': res['steps'],
            'prog': prog, 'validate': v}


def jit_run(src):
    toks = lex(src)
    ast = parse(toks)
    prog = compile_s(ast)
    J = jit(prog)
    L = J['run']()
    return {'env': L, 'prog': prog, 'jit': J}


__all__ = ['lex', 'parse', 'compile_s', 'validate_s', 'validate_one',
           'exec_s', 'assemble', 'disasm', 'jit', 'run', 'jit_run',
           'plane', 'dispatch_all', 'OPS', 'OP', 'E', 'NIL', 'RULES']
