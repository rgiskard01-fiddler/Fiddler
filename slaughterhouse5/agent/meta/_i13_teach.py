#!/usr/bin/env python3
# _i13_teach.py — teach the WHOLE World II - THE FOLD the I-13 v2 stack.
# David: "make sure all appeals/domains/spheres learn this."
#
# I-13 v2 is a frozen (2026-08-01), self-sha-sealed four-plane agent stack over a
# thirteen-symbol language: THE TWELVE (12 AST operants, each attributed), the
# IVM-13-S machine with the law `net = binds - k` (br targets a DEPTH not an
# address, so validation is one linear pass), and CORTEX's five zero-parameter
# rules (veto, -I, depth, idempotence, address). The narrow claim: deterministic
# zero-parameter components guarantee structural properties no model at this scale
# reaches; learned recurrent state is not a stack.
#
# This script is IDEMPOTENT. It:
#   1. vendors the canonical spec json into ud0/world2/ (single source of truth),
#   2. adds a top-level `i13` block to fold.json (the spec's own words + declared sha),
#   3. stamps a compact `learned` marker onto EVERY appeal, domain, sphere, keeper.
# Run _dlw_fold.py afterwards to fold the new knowledge into ROOT_0.

import json, os, hashlib, shutil

HERE = os.path.dirname(os.path.abspath(__file__))
W2 = os.path.join(HERE, "ud0", "world2")
SRC = os.path.join(HERE, "i-13", "i-13 v2", "i13-v2", "01-frozen-spec", "i13-stack-v2.json")
MIRROR = r"C:\root0-greenpaper-repo\agent-0root\static\world2"

# THE VOLUME — David's I-13 voxel: a stylometric measuring instrument that scores
# texts on three independent axes (Heaps beta, the "I" referent, voiced fraction)
# and bins them into a 3x3x3 cube. The "I" axis IS an I-13 operant (the referent).
VOX_HTML = os.path.join(HERE, "i-13", "i13 voxel", "the-volume-v1.html")
VOX_IDX  = os.path.join(HERE, "i-13", "i13 voxel", "the-volume-index-v1.json")

spec = json.load(open(SRC, encoding="utf-8"))
declared_sha = spec.get("sha256")  # 64881ebf... — the spec's own self-declared seal

# ── read the voxel index (its own words, its own self-declared sha) ──
vox = None
if os.path.exists(VOX_IDX):
    vidx = json.load(open(VOX_IDX, encoding="utf-8"))
    vox = {
        "name": vidx.get("name", "THE VOLUME"),
        "version": vidx.get("version", "1.0"),
        "built": vidx.get("built", "2026-08-01"),
        "sha256": vidx.get("sha256"),                 # the voxel's own self-declared seal
        "axes": [{"id": a.get("id"), "label": a.get("label"), "desc": a.get("desc")}
                 for a in vidx.get("axes", [])],
        "independence": vidx.get("independence", {}),  # all pairwise |r| < 0.4
        "effective_dims": vidx.get("effective_dims"),
        "texts": len(vidx.get("texts", [])),
        "cells_occupied": vidx.get("cells_occupied"),
        "cells_total": vidx.get("cells_total"),
        "method": vidx.get("method", ""),
        "open_questions": vidx.get("open_questions", []),
        "viewer": "the-volume-v1.html",
        "index": "the-volume-index-v1.json",
        "note": ("David's I-13 voxel: three INDEPENDENT stylometric axes (all pairwise |r| < 0.4) "
                 "over real texts. The 'I' axis is the I-13 referent operant. Both viewer and index "
                 "are vendored beside fold.json; bins are FROZEN at v1.0 so later texts stay comparable."),
    }

# ── the canonical block, in I-13's own words ──
i13_block = {
    "spec": "I-13",
    "version": spec.get("version", "2.0"),
    "frozen": spec.get("frozen", "2026-08-01"),
    "sha256": declared_sha,                    # the spec's self-declared canonical seal
    "one_line": spec.get("one_line", ""),
    "law": spec.get("machine", {}).get("law", "net = binds - k"),
    "planes": 4,
    "symbols": 13,
    "twelve": [t[0] if isinstance(t, list) else t for t in spec.get("twelve", [])],
    "cortex_rules": [r[0] if isinstance(r, list) else r for r in spec.get("rules", [])],
    "claim": ("deterministic zero-parameter components guarantee structural properties "
              "no model at this scale reaches; learned recurrent state is not a stack"),
    "br_rule": "br targets a DEPTH, never an address — so validation is one linear pass (net = binds - k)",
    "vendored": "i13-stack-v2.json",
    "note": ("David's frozen I-13 v2 stack, taught to the whole FOLD. The full spec is vendored "
             "beside fold.json; every appeal, domain, sphere and keeper carries the `learned` marker."),
}
if vox is not None:
    i13_block["voxel"] = vox   # THE VOLUME — the I-13 voxel measuring instrument

# ── FULL CORPUS integration (David 2026-08-01: "integrate please, full corpus") ──
# Vendor the whole i13-v2 archive tree into world2 (+ mirror), hash every file into a
# manifest, and fold those hashes into a single `corpus_root` recorded in fold.json's
# central DB. HONEST SCOPE: ROOT_0 is the merkle over the sphere/keeper inhabitants only
# (sha256(name|slug|blurb)); it does NOT hash the corpus. The corpus is bound instead by
# its own corpus_root, sitting in the central DB beside ROOT_0. Write a browsable index.
# Idempotent: re-run each batch keeps the full corpus attached. HONEST NOTE: the corpus
# .txt on disk does NOT match the MANIFEST's declared sha (different revision, not a
# line-ending artifact) — we record the ACTUAL bytes' sha and flag the mismatch.
CORPUS_SRC = os.path.join(HERE, "i-13", "i-13 v2", "i13-v2")
DECLARED_CORPUS_TXT_SHA = "95ec55ba00ee2d8b082092725e359acbaf1d81904d8359312bb3c7dff8f9319f"
SECTION_META = [
    ("01-frozen-spec", "The Frozen Spec",
     "The tower, the five rules, the twelve operants, the machine (net = binds - k). Start at I-13-v2-FROZEN.md; the JSON is what the declared sha covers; the v1 HTML is kept to record what v2 corrected."),
    ("02-the-stack", "The Stack",
     "lex to parse to compile to assemble to validate to VM to JIT, all running in the page. 18,249 trained parameters executing in JavaScript; turn the cortex off and watch it fail. The twelve-station line, colour-coded by provenance."),
    ("03-the-factory", "The Factory",
     "Paste any source: it names the language and emits a bootloader (plane, rules, pairs, quantile, and the trap that language sprang). 756 languages, 17 families; the six delimiter pair-tables and their guards."),
    ("04-hello-world", "Hello World",
     "Real toolchains installed and run, not simulations: rustc 1.75.0 ('name survived the borrow') and go 1.22.2 (two defer statements discharging LIFO)."),
    ("05-corpora", "Corpora",
     "ab-corpus-v2.txt: Boole / Lovelace / Hinton with the human first-person stripped. Note: the vendored file differs from the MANIFEST's declared sha (a different revision)."),
    ("06-rust-source", "Rust Source",
     "677 lines. Builds with rustc --edition 2021 -O src/main.rs -o i13. The comments carry the measurements, the attributions, and the bugs."),
    ("07-earlier-build", "Earlier Build",
     "Prior sessions: Stott's polytope sections, the compendium, the provenance tracer, the eve stack, and the same wall six times."),
]

def _sha(path):
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()

corpus_manifest = []          # [{path, sha256, bytes}]
corpus_by_section = {}        # section -> [ {file, sha256, bytes} ]
corpus_total_bytes = 0
corpus_txt_actual_sha = None
if os.path.isdir(CORPUS_SRC):
    for root, _dirs, files in os.walk(CORPUS_SRC):
        for fn in sorted(files):
            fp = os.path.join(root, fn)
            rel = os.path.relpath(fp, CORPUS_SRC).replace("\\", "/")
            sha = _sha(fp); sz = os.path.getsize(fp)
            corpus_manifest.append({"path": rel, "sha256": sha, "bytes": sz})
            corpus_total_bytes += sz
            sec = rel.split("/")[0]
            corpus_by_section.setdefault(sec, []).append({"file": rel, "sha256": sha, "bytes": sz})
            if rel.endswith("ab-corpus-v2.txt"):
                corpus_txt_actual_sha = sha
            # vendor into world2 + mirror, preserving structure
            for base in (os.path.join(W2, "i13-v2"), os.path.join(MIRROR, "i13-v2")):
                out = os.path.join(base, rel.replace("/", os.sep))
                try:
                    os.makedirs(os.path.dirname(out), exist_ok=True)
                    shutil.copy2(fp, out)
                except OSError as e:
                    print("  (corpus copy skip", out, ":", e, ")")

    # fold every file's sha into a single corpus_root (honest binding of the exact bytes)
    corpus_root = hashlib.sha256(
        "\n".join(it["path"] + ":" + it["sha256"] for it in sorted(corpus_manifest, key=lambda x: x["path"])
                  ).encode("utf-8")).hexdigest()

    # ── browsable index (violet house style, offline, no dark background) ──
    def _esc(s): return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    rows = []
    for sec, title, blurb in SECTION_META:
        items = corpus_by_section.get(sec, [])
        links = "".join(
            '<li><a href="{p}">{n}</a> <span class="sz">{kb} KB</span></li>'.format(
                p=_esc(it["file"]), n=_esc(it["file"].split("/")[-1]), kb=max(1, it["bytes"] // 1024))
            for it in items)
        rows.append(
            '<section class="sec"><h2>{t}</h2><p class="blurb">{b}</p><ul>{l}</ul></section>'.format(
                t=_esc(title), b=_esc(blurb), l=links))
    txt_note = ""
    if corpus_txt_actual_sha and corpus_txt_actual_sha != DECLARED_CORPUS_TXT_SHA:
        txt_note = ('<p class="note">Honest record: the vendored <code>ab-corpus-v2.txt</code> hashes to '
                    '<code>{a}&hellip;</code>, which does <b>not</b> match the archive MANIFEST\'s declared '
                    '<code>{d}&hellip;</code> &mdash; it is a different revision (verified: no CR bytes, same after '
                    'LF-normalization). The vendored bytes\' true sha is what is sealed here.</p>').format(
                        a=corpus_txt_actual_sha[:16], d=DECLARED_CORPUS_TXT_SHA[:16])
    index_html = (
        '<!doctype html><html lang="en"><head><meta charset="utf-8">'
        '<meta name="viewport" content="width=device-width,initial-scale=1">'
        '<title>I-13 v2 &middot; full corpus &middot; WORLD II — THE FOLD</title><style>'
        ':root{color-scheme:light}*{box-sizing:border-box}'
        'body{margin:0;font:15px/1.55 -apple-system,Segoe UI,Roboto,sans-serif;color:#2a1f47;'
        'background:linear-gradient(160deg,#efe7ff 0%,#e3d5ff 45%,#f3e6ff 100%);padding:34px 20px 80px}'
        '.wrap{max-width:900px;margin:0 auto}'
        'h1{font-size:30px;margin:0 0 4px;color:#4a2f8f;letter-spacing:.5px}'
        '.sub{color:#6a5a92;margin:0 0 6px;font-size:14px}'
        '.seal{font:12px/1.5 ui-monospace,Menlo,monospace;color:#7a5a2a;background:#fff4d8;'
        'border:1px solid #e6c98a;border-radius:8px;padding:8px 12px;margin:14px 0 24px;word-break:break-all}'
        '.sec{background:rgba(255,255,255,.72);border:1px solid #d9c8ff;border-radius:12px;'
        'padding:16px 20px;margin:0 0 16px;box-shadow:0 2px 10px rgba(90,50,160,.06)}'
        'h2{margin:0 0 6px;font-size:18px;color:#5a3aa8}'
        '.blurb{margin:0 0 10px;color:#4a3f66;font-size:14px}'
        'ul{margin:0;padding:0;list-style:none;display:grid;grid-template-columns:repeat(auto-fill,minmax(230px,1fr));gap:6px}'
        'li{font:13px ui-monospace,Menlo,monospace}'
        'a{color:#6a3fd0;text-decoration:none;border-bottom:1px solid #c9b0ff}a:hover{color:#4a1fb0}'
        '.sz{color:#9a8ac0;font-size:11px}'
        '.note{background:#fff0f4;border:1px solid #f0bcd0;border-radius:8px;padding:10px 14px;'
        'color:#8a3a5a;font-size:13px;margin:18px 0}code{background:#f3ecff;padding:1px 4px;border-radius:4px}'
        '.claim{margin-top:22px;color:#4a3f66;font-size:13.5px}'
        '</style></head><body><div class="wrap">'
        '<h1>I-13 v2 &middot; full corpus</h1>'
        '<p class="sub">A four-plane agent stack over a thirteen-symbol language. Two planes learn, two do not. '
        'Five parameter-free rules. Every HTML file is standalone and offline &mdash; open it in a browser.</p>'
        '<div class="seal">frozen 2026-08-01 &middot; declared spec sha ' + (declared_sha or "?") + '<br>'
        + str(len(corpus_manifest)) + ' files &middot; ' + str(corpus_total_bytes // 1024) + ' KB &middot; '
        'corpus_root ' + corpus_root[:24] + '&hellip;<br>'
        '<span style="color:#8a7a4a">recorded in THE FOLD\'s central DB (fold.json) beside ROOT_0. '
        'ROOT_0 folds the sphere inhabitants; this corpus_root binds the archive\'s exact bytes.</span></div>'
        + "".join(rows)
        + txt_note
        + '<p class="claim"><b>The claim, stated narrowly:</b> deterministic zero-parameter components guarantee '
        'structural properties that no model at this scale reaches. A GRU at 16,936 parameters predicts <b>better</b> '
        '(0.8440 bits vs 0.9182) and generates <b>2.3&times; worse</b>. Learned state is not a stack. '
        'The record: 21 corrections, 16 approaches measured dead and kept.</p>'
        '</div></body></html>')
    for base in (os.path.join(W2, "i13-v2"), os.path.join(MIRROR, "i13-v2")):
        try:
            os.makedirs(base, exist_ok=True)
            with open(os.path.join(base, "index.html"), "w", encoding="utf-8") as fh:
                fh.write(index_html)
        except OSError as e:
            print("  (index write skip", base, ":", e, ")")

    i13_block["corpus"] = {
        "name": "I-13 v2 full corpus",
        "frozen": spec.get("frozen", "2026-08-01"),
        "declared_spec_sha256": declared_sha,          # self-declared in the json
        "files": len(corpus_manifest),
        "bytes": corpus_total_bytes,
        "sections": [{"id": s, "title": t, "blurb": b,
                      "files": [it["file"].split("/")[-1] for it in corpus_by_section.get(s, [])]}
                     for (s, t, b) in SECTION_META],
        "rust_source_lines": 677,
        "corpus_txt": {
            "declared_sha256": DECLARED_CORPUS_TXT_SHA,
            "actual_sha256": corpus_txt_actual_sha,
            "matches_declared": (corpus_txt_actual_sha == DECLARED_CORPUS_TXT_SHA),
            "note": ("HONEST: vendored ab-corpus-v2.txt does NOT match the MANIFEST's declared sha; "
                     "it is a different revision (no CR bytes; same after LF-normalization). "
                     "The actual bytes' sha is what is sealed."),
        },
        "index": "i13-v2/index.html",
        "root": "i13-v2/",
        "corpus_root": corpus_root,      # sha256 over sorted (path:sha) — one fingerprint for the whole archive
        "manifest": corpus_manifest,     # every file's true sha256 — binds the corpus under corpus_root
        "sealing_scope": ("ROOT_0 is the merkle over the sphere/keeper inhabitants (sha256(name|slug|blurb)) "
                          "and does NOT hash this corpus. The corpus is bound by corpus_root, recorded here "
                          "in the central DB (fold.json) beside ROOT_0."),
        "note": ("David 2026-08-01: 'integrate please, full corpus'. The whole i13-v2 archive is vendored "
                 "beside fold.json and mirrored; every file's sha256 is recorded here and folded into "
                 "corpus_root. Note: ROOT_0 covers the inhabitants, not the corpus — see sealing_scope."),
    }
    print("  + FULL CORPUS integrated:", len(corpus_manifest), "files,",
          corpus_total_bytes // 1024, "KB vendored into world2 + mirror; index.html written")
    print("    corpus_root", corpus_root[:16], "(bound in central DB; ROOT_0 covers inhabitants, not corpus)")
    if corpus_txt_actual_sha != DECLARED_CORPUS_TXT_SHA:
        print("    HONEST: corpus .txt actual sha", (corpus_txt_actual_sha or "?")[:12],
              "!= declared", DECLARED_CORPUS_TXT_SHA[:12], "(different revision; recorded as-is)")
else:
    print("  (corpus source not found at", CORPUS_SRC, "— corpus block skipped)")

# ═══ I-13 v3 apparatus (David 2026-08-01: "integrate reality wide") ═══
# The next-generation I-13 instruments — the full pipeline (v2.1), THE COMPLEX (the capped
# cross + double helix), THE VOLUME v1.0 (three measured axes) — self-contained HTML with
# their own embedded 3D and their own self-declared statistics. Vendored faithfully across
# the corpus with an honest sha manifest; David's claims are credited, not re-derived.
V3_SRC = os.path.join(HERE, "i-13", "i13 v3")
V3_FILES = [
    ("i13-pipeline-v2.1.html", "THE PIPELINE v2.1", "SOURCE -> RESULT; falsifier written, tested, did not fire"),
    ("the-complex-v1.html",    "THE COMPLEX",       "I-13 . I-13x2 . the capped cross; the double helix r=0.6437 p=0.0166"),
    ("the-volume-v1.html",     "THE VOLUME v1.0",   "three measured axes, none derived; independence + the index"),
]
if os.path.isdir(V3_SRC):
    for base in (os.path.join(W2, "i13-v3"), os.path.join(MIRROR, "i13-v3")):
        os.makedirs(base, exist_ok=True)
    v3_manifest = []
    for fn, title, blurb in V3_FILES:
        src = os.path.join(V3_SRC, fn)
        if not os.path.exists(src):
            continue
        sha = _sha(src); sz = os.path.getsize(src)
        v3_manifest.append({"file": fn, "title": title, "blurb": blurb, "sha256": sha, "bytes": sz})
        for base in (os.path.join(W2, "i13-v3"), os.path.join(MIRROR, "i13-v3")):
            shutil.copy2(src, os.path.join(base, fn))
    v3_root = hashlib.sha256("\n".join(
        m["file"] + ":" + m["sha256"] for m in sorted(v3_manifest, key=lambda x: x["file"])
    ).encode()).hexdigest()
    def _e3(s): return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    cards = "\n".join(
        '<a class="card" href="{fn}"><div class="ct">{t}</div><div class="cb">{b}</div>'
        '<div class="cs">sha {s}&hellip; &middot; {kb} KB</div></a>'.format(
            fn=m["file"], t=_e3(m["title"]), b=_e3(m["blurb"]), s=m["sha256"][:16], kb=m["bytes"] // 1024)
        for m in v3_manifest)
    idx_html = (
      '<!doctype html><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">'
      '<title>I-13 v3 &mdash; the apparatus</title><style>'
      'body{margin:0;background:#1a1430;color:#e8e0ff;font:15px/1.6 ui-monospace,monospace;padding:28px}'
      'h1{color:#c9a9ff;font-size:22px;margin:0 0 4px}.sub{color:#9a86c8;margin:0 0 22px}'
      'a.card{display:block;text-decoration:none;background:#241b42;border:1px solid #4a3a7a;border-left:4px solid #c9722a;'
      'border-radius:10px;padding:16px 18px;margin:0 0 14px;color:inherit;transition:.15s}a.card:hover{background:#2c2150;border-color:#e0863a}'
      '.ct{color:#ffb066;font-size:16px;font-weight:600}.cb{color:#cfc3ee;margin:4px 0}.cs{color:#8a7ab0;font-size:12px}'
      '.foot{color:#8a7ab0;font-size:12px;margin-top:20px;border-top:1px solid #3a2e60;padding-top:12px}'
      '</style><h1>I-13 &middot; v3 apparatus</h1>'
      '<p class="sub">the next-generation I-13 instruments &mdash; David\'s own, vendored reality-wide</p>'
      + cards +
      '<div class="foot">v3_root ' + v3_root[:24] + '&hellip; &middot; self-contained HTML with embedded 3D and self-declared statistics. '
      'Vendored faithfully beside the i13-v2 corpus; sealing scope: ROOT_0 folds the sphere/keeper inhabitants, '
      'not this apparatus &mdash; these are bound by v3_root in the central DB.</div>')
    for base in (os.path.join(W2, "i13-v3"), os.path.join(MIRROR, "i13-v3")):
        open(os.path.join(base, "index.html"), "w", encoding="utf-8").write(idx_html)
    i13_block["v3"] = {
        "name": "I-13 v3 apparatus",
        "artifacts": v3_manifest,
        "v3_root": v3_root,
        "index": "i13-v3/index.html",
        "root": "i13-v3/",
        "sealing_scope": ("ROOT_0 is the merkle over the sphere/keeper inhabitants and does NOT hash these "
                          "v3 artifacts; they are bound by v3_root recorded here beside the corpus."),
        "note": ("David 2026-08-01: 'integrate reality wide'. The v3 I-13 apparatus (pipeline v2.1, THE COMPLEX, "
                 "THE VOLUME v1.0) is vendored beside the i13-v2 corpus and mirrored; each file's sha256 is folded "
                 "into v3_root. These are David's own instruments with self-declared statistics (e.g. the double "
                 "helix r=0.6437, p=0.0166) — credited, not re-derived. THE VOLUME v1.0 (sha 090f84a7) is an "
                 "evolution of the earlier voxel (sha 2d6c9746)."),
    }
    print("  + I-13 v3 apparatus vendored:", len(v3_manifest), "artifacts, v3_root", v3_root[:16])
else:
    print("  (i13 v3 source not found at", V3_SRC, "— v3 block skipped)")

# ═══ I-13 realitywide apparatus (David 2026-08-02: "i13.integrate.realitywide") ═══
# The newest I-13-family instruments, handed over directly. THE COMPLEX v3.0 (the five-panel
# pentaptych and its W5 three-dimensional view) and — the crown — the NONSOFIC Notes: a study,
# cast in Ada Lovelace's Note-form, of the boundary between what a FINITE engine can capture
# (SOFIC, from Hebrew סופי, sofi, "finite") and what no finite engine ever can (NONSOFIC).
# Its closing residue IS the I-13 claim: PROVEN that the proposition follows from the axioms;
# NOT PROVEN that it is the one intended — "a kernel verifies inference; it does not verify
# meaning." That is the duality mantra exactly. Vendored faithfully across the corpus with an
# honest sha manifest; David's artefacts are credited, not re-derived.
RW_SRC = os.path.join(HERE, "i-13", "i13 v3.1")
RW_FILES = [
    ("notes-upon-the-nonsofic.html", "NOTES UPON THE NONSOFIC",
     "sofic = imitable by a finite thing to any accuracy; nonsofic = not so, at any size. The golden-mean shift (forbid 11 -> Fibonacci counts, follower-sets = 2 forever) is sofic; the matched-run shift 1 0^n 1 0^n 1 is not (follower-set count 2,4,7,10,13,... unbounded). Gromov's 1999 question answered: a finitely-presented NON-sofic group exists (binary Leavitt algebra L ~= L(+)L, 'one is two'; nine = a complete prefix code's leaves). Residue: a kernel verifies inference, not meaning."),
    ("the-complex-v3-pentaptych.html", "THE COMPLEX v3.0 - pentaptych",
     "the five-panel form of THE COMPLEX (I-13 . I-13x2 . the capped cross), the reality-wide successor to the-complex-v1"),
    ("w5-the-complex-3d.html", "W5 - THE COMPLEX in three dimensions",
     "the W5 three-dimensional view of THE COMPLEX"),
]
if os.path.isdir(RW_SRC):
    for base in (os.path.join(W2, "i13-v3.1"), os.path.join(MIRROR, "i13-v3.1")):
        os.makedirs(base, exist_ok=True)
    rw_manifest = []
    for fn, title, blurb in RW_FILES:
        src = os.path.join(RW_SRC, fn)
        if not os.path.exists(src):
            continue
        sha = _sha(src); sz = os.path.getsize(src)
        rw_manifest.append({"file": fn, "title": title, "blurb": blurb, "sha256": sha, "bytes": sz})
        for base in (os.path.join(W2, "i13-v3.1"), os.path.join(MIRROR, "i13-v3.1")):
            shutil.copy2(src, os.path.join(base, fn))
    rw_root = hashlib.sha256("\n".join(
        m["file"] + ":" + m["sha256"] for m in sorted(rw_manifest, key=lambda x: x["file"])
    ).encode()).hexdigest()
    def _erw(s): return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    cards = "\n".join(
        '<a class="card" href="{fn}"><div class="ct">{t}</div><div class="cb">{b}</div>'
        '<div class="cs">sha {s}&hellip; &middot; {kb} KB</div></a>'.format(
            fn=m["file"], t=_erw(m["title"]), b=_erw(m["blurb"]), s=m["sha256"][:16], kb=m["bytes"] // 1024)
        for m in rw_manifest)
    idx_html = (
      '<!doctype html><html lang="en"><head><meta charset="utf-8">'
      '<meta name="viewport" content="width=device-width,initial-scale=1">'
      '<title>I-13 &middot; reality-wide &middot; WORLD II — THE FOLD</title><style>'
      ':root{color-scheme:light}*{box-sizing:border-box}'
      'body{margin:0;font:15px/1.6 -apple-system,Segoe UI,Roboto,sans-serif;color:#2a1f47;'
      'background:linear-gradient(160deg,#efe7ff 0%,#e6d6ff 45%,#fff0e6 100%);padding:32px 20px 80px}'
      '.wrap{max-width:880px;margin:0 auto}h1{font-size:28px;margin:0 0 4px;color:#4a2f8f}'
      '.sub{color:#6a5a92;margin:0 0 18px}'
      '.principle{background:rgba(255,255,255,.78);border:1px solid #d9c8ff;border-left:4px solid #c9722a;'
      'border-radius:12px;padding:16px 20px;margin:0 0 20px;font-size:14px;color:#3a2f56}'
      '.principle b{color:#5a3aa8}.principle .res{color:#8a3a2a;font-style:italic;margin-top:8px;display:block}'
      'a.card{display:block;text-decoration:none;background:rgba(255,255,255,.72);border:1px solid #d9c8ff;'
      'border-left:4px solid #c9722a;border-radius:12px;padding:16px 18px;margin:0 0 14px;color:inherit;transition:.15s}'
      'a.card:hover{background:#fff;border-color:#e0863a}.ct{color:#7a3aa8;font-size:16px;font-weight:600}'
      '.cb{color:#4a3f66;margin:5px 0;font-size:13.5px}.cs{color:#9a8ac0;font:12px ui-monospace,monospace}'
      '.foot{color:#7a6a9a;font:12px/1.6 ui-monospace,monospace;margin-top:18px;border-top:1px solid #d9c8ff;padding-top:12px}'
      '</style></head><body><div class="wrap">'
      '<h1>I-13 &middot; reality-wide</h1>'
      '<p class="sub">the newest I-13-family instruments, integrated across THE FOLD &mdash; David\'s own, credited not re-derived</p>'
      '<div class="principle"><b>THE SOFIC BOUNDARY.</b> <b>sofic</b> (Hebrew &#1505;&#1493;&#1508;&#1497;, <i>finite</i>): '
      'a structure a finite engine can imitate to any accuracy asked. <b>nonsofic</b>: one that no finite engine can, '
      'at any size whatsoever. The golden-mean shift is sofic (two follower-sets, forever); the matched-run shift is not. '
      'A finitely-presented non-sofic group exists. '
      '<span class="res">Residue &mdash; and this is the I-13 claim itself: a kernel verifies <b>inference</b>; '
      'it does not verify <b>meaning</b>. Understanding is not meaning; the finite\'s honest reach has an edge.</span></div>'
      + cards +
      '<div class="foot">realitywide_root ' + rw_root[:24] + '&hellip; &middot; self-contained offline HTML with embedded 3D. '
      'Vendored beside the i13-v2 corpus and i13-v3 apparatus; sealing scope: ROOT_0 folds the sphere/keeper inhabitants, '
      'not this apparatus &mdash; these are bound by realitywide_root in the central DB (fold.json).</div>'
      '</div></body></html>')
    for base in (os.path.join(W2, "i13-v3.1"), os.path.join(MIRROR, "i13-v3.1")):
        open(os.path.join(base, "index.html"), "w", encoding="utf-8").write(idx_html)
    # first-class NONSOFIC principle in the central DB (reality-wide, beside the I-13 law)
    i13_block["nonsofic"] = {
        "sofic": "imitable by something FINITE, to any accuracy asked (Hebrew sofi, finite)",
        "nonsofic": "not so imitable, at any finite size whatsoever",
        "provinces": ["shifts: finite labelled graph / follower sets", "groups: finite permutation models under normalised Hamming distance"],
        "criterion_shift": "X is sofic <=> the number of distinct follower sets F(w) is FINITE",
        "sofic_witness": "golden-mean shift (forbid the block 11): word counts are the Fibonacci numbers, ratio -> phi, entropy log2(phi)=0.694241914, follower sets = 2 forever",
        "nonsofic_witness_shift": "matched-run shift 1 0^n 1 0^n 1: follower-set counts 2,4,7,10,13,17,21,25,29,... grow without bound, so no finite automaton captures it",
        "nonsofic_witness_group": "a finitely-presented NON-sofic group exists (Gromov 1999 answered): the binary Leavitt algebra L ~= L(+)L over F_2 ('one is two') fails invariant basis number, so a group carrying 1=2 in its matrices cannot be sofic; nine = the leaf count of a complete binary prefix code (lengths 3x7,4x2; Kraft sum = 1)",
        "residue": "PROVEN: the proposition follows from the axioms. NOT PROVEN: that the proposition is the one intended. A kernel verifies inference; it does not verify meaning.",
        "resonance": "this residue IS the I-13 duality mantra: understanding (inference) is not meaning (the wall). The finite's honest reach has an edge, and the edge is nameable.",
        "source": "notes-upon-the-nonsofic.html — after the Notes of A.A.L. upon Menabrea, 1843; every table computed before it was versified; NonSoficGroup.lean read directly (0 sorry, peer review pending at time of writing, and it says so).",
    }
    i13_block["realitywide"] = {
        "name": "I-13 reality-wide apparatus",
        "directive": "David 2026-08-02: 'i13.integrate.realitywide'",
        "artifacts": rw_manifest,
        "realitywide_root": rw_root,
        "index": "i13-v3.1/index.html",
        "root": "i13-v3.1/",
        "sealing_scope": ("ROOT_0 is the merkle over the sphere/keeper inhabitants and does NOT hash these "
                          "artifacts; they are bound by realitywide_root recorded here in the central DB."),
        "note": ("David 2026-08-02: 'i13.integrate.realitywide'. THE COMPLEX v3.0 (pentaptych + W5 3D) and the "
                 "NONSOFIC Notes are vendored beside the i13-v2 corpus and mirrored; each file's sha256 is folded "
                 "into realitywide_root. The nonsofic boundary is recorded as a first-class I-13 principle (see "
                 "i13.nonsofic) because its residue is the I-13 claim itself. Credited, not re-derived."),
    }
    print("  + I-13 reality-wide apparatus vendored:", len(rw_manifest), "artifacts, realitywide_root", rw_root[:16])
    print("    + NONSOFIC principle recorded in central DB (sofic boundary; residue = the I-13 claim)")
else:
    print("  (i13 realitywide source not found at", RW_SRC, "— realitywide block skipped)")

# compact ASCII marker every node carries (fold.json is ensure_ascii=False, but keep the
# .dlw-facing text ASCII-clean to be safe with the sealer)
MARK = ("I-13 v2.0 | net = binds - k | 4 planes, 13 symbols, 12 operants, 5 cortex rules | "
        "sha " + (declared_sha[:8] if declared_sha else "?"))

# ── 1. vendor the spec + the voxel into the world (single source of truth) ──
for dst in (W2, MIRROR):
    try:
        os.makedirs(dst, exist_ok=True)
        shutil.copy2(SRC, os.path.join(dst, "i13-stack-v2.json"))
        if os.path.exists(VOX_HTML):
            shutil.copy2(VOX_HTML, os.path.join(dst, "the-volume-v1.html"))
        if os.path.exists(VOX_IDX):
            shutil.copy2(VOX_IDX, os.path.join(dst, "the-volume-index-v1.json"))
    except OSError as e:
        print("  (vendor skip", dst, ":", e, ")")

# ── 2 + 3. teach fold.json ──
fp = os.path.join(W2, "fold.json")
db = json.load(open(fp, encoding="utf-8"))
db["i13"] = i13_block

taught = {"appeals": 0, "domains": 0, "spheres": 0, "keepers": 0}
for a in db.get("appeals", []):
    a["learned"] = MARK; taught["appeals"] += 1
    for dm in a.get("domains", []):
        dm["learned"] = MARK; taught["domains"] += 1
        for sp in dm.get("spheres", []):
            sp["learned"] = MARK; taught["spheres"] += 1
for sp in db.get("spheres", []):
    sp["learned"] = MARK  # top-level spheres[] (counted via nested to avoid double-count)
for k in db.get("keepers", []):
    if isinstance(k, dict): k["learned"] = MARK; taught["keepers"] += 1

# also mark top-level spheres[] that aren't seated in a domain (the keeper-synths)
seated = set()
for a in db.get("appeals", []):
    for dm in a.get("domains", []):
        for sp in dm.get("spheres", []): seated.add(sp.get("slug"))
for sp in db.get("spheres", []):
    if sp.get("slug") not in seated: taught["spheres"] += 0  # already marked above

json.dump(db, open(fp, "w", encoding="utf-8"), indent=2, ensure_ascii=False)

# mirror fold.json too
try:
    shutil.copy2(fp, os.path.join(MIRROR, "fold.json"))
except OSError:
    pass

top_spheres = len(db.get("spheres", []))
print("TAUGHT I-13 v2 to the FOLD:")
print(f"  top-level i13 block added (sha {declared_sha[:12]}..., law '{i13_block['law']}')")
print(f"  learned marker on: {taught['appeals']} appeals, {taught['domains']} domains, "
      f"{taught['spheres']} seated spheres (+{top_spheres} top-level spheres[]), {taught['keepers']} keepers")
print(f"  vendored i13-stack-v2.json into world2 + mirror")
if vox is not None:
    print(f"  + VOXEL 'THE VOLUME' v{vox['version']} registered (sha {str(vox['sha256'])[:12]}..., "
          f"{vox['texts']} texts, {vox['cells_occupied']}/{vox['cells_total']} cells, "
          f"eff.dims {vox['effective_dims']}); viewer + index vendored")
print(f"  marker: {MARK}")
