#!/usr/bin/env python3
"""Audit citations and the bibliography of a LaTeX paper.

Citation errors are the ones that never raise a warning: BibTeX silently
drops an entry that contains a '%' comment, a key cited in a float gets its
number when the float is declared rather than where it lands, an author list
of seven gets printed in full or one of five gets cut to "et al.". This script
checks what the compiler will not:

  * every \\cite key resolves to a .bib entry, and every .bib entry that made
    it into the .bbl is cited at least once
  * the context (~80 chars) in which each key is cited, so a wrong key beside
    a method name is visible at a glance
  * IEEE's author rule: more than six authors -> first author + "et al."
    (i.e. "and others" in the .bib); six or fewer -> list them all
  * entries missing a year, or missing pages when they are not arXiv/misc
  * duplicate titles
  * '%' inside an @entry{...} block, which makes BibTeX skip the whole entry
  * .bbl item count vs. the number of distinct cited keys

Usage:
  check_citations.py --main main.tex [--bbl main.bbl] [--bib refs.bib ...]
  (bib files default to the ones named in \\bibliography{...})
"""
import argparse, os, re, sys


def discover_inputs(main_tex):
    seen, out = set(), []
    base = os.path.dirname(os.path.abspath(main_tex))

    def walk(p):
        p = os.path.abspath(p)
        if p in seen or not os.path.exists(p):
            return
        seen.add(p); out.append(p)
        src = re.sub(r"(?m)^\s*%.*$", "", open(p, errors="ignore").read())
        for m in re.finditer(r"\\(?:input|include)\{([^}]+)\}", src):
            t = m.group(1).strip()
            t = t if t.endswith(".tex") else t + ".tex"
            walk(t if os.path.isabs(t) else os.path.join(base, t))
    walk(main_tex)
    return out


def parse_bib(path):
    """Very small .bib parser: returns {key: {field: value}} plus a list of
    keys whose entry body contains a '%' line (BibTeX will skip them)."""
    text = open(path, errors="ignore").read()
    entries, percent_inside = {}, []
    for m in re.finditer(r"@(\w+)\s*\{\s*([^,\s]+)\s*,", text):
        etype, key = m.group(1).lower(), m.group(2)
        # find the matching closing brace of this entry
        i = m.end() - 1
        depth, j = 0, m.start()
        for j in range(text.index("{", m.start()), len(text)):
            if text[j] == "{":
                depth += 1
            elif text[j] == "}":
                depth -= 1
                if depth == 0:
                    break
        body = text[m.end():j]
        if re.search(r"(?m)^\s*%", body):
            percent_inside.append(key)
        fields = {}
        for fm in re.finditer(r"(\w+)\s*=\s*(\{(?:[^{}]|\{[^{}]*\})*\}|\"[^\"]*\"|[^,\n]+)", body):
            v = fm.group(2).strip().strip(",").strip()
            if v[:1] in "{\"":
                v = v[1:-1]
            fields[fm.group(1).lower()] = re.sub(r"\s+", " ", v)
        fields["_type"] = etype
        entries[key] = fields
    return entries, percent_inside


def author_count(author_field):
    if not author_field:
        return 0
    parts = [p.strip() for p in re.split(r"\s+and\s+", author_field)]
    return len(parts), any(p.lower() == "others" for p in parts)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--main", required=True)
    ap.add_argument("--bbl")
    ap.add_argument("--bib", nargs="*")
    ap.add_argument("--max-authors", type=int, default=6, help="IEEE: list all authors up to this many, else et al.")
    ap.add_argument("--quiet-contexts", action="store_true", help="do not print the citation contexts")
    a = ap.parse_args()

    base = os.path.dirname(os.path.abspath(a.main))
    tex_files = discover_inputs(a.main)
    main_src = open(a.main, errors="ignore").read()

    bibs = a.bib
    if not bibs:
        m = re.search(r"\\bibliography\{([^}]+)\}", main_src)
        bibs = [os.path.join(base, b.strip() + ("" if b.strip().endswith(".bib") else ".bib"))
                for b in m.group(1).split(",")] if m else []
    bbl = a.bbl or os.path.splitext(a.main)[0] + ".bbl"

    # ---- cites with context -----------------------------------------------
    uses = {}
    for f in tex_files:
        src = open(f, errors="ignore").read()
        src_nc = re.sub(r"(?m)^\s*%.*$", "", src)
        for m in re.finditer(r"\\cite[tp]?\*?(?:\[[^\]]*\])?\{([^}]*)\}", src_nc):
            ctx = re.sub(r"\s+", " ", src_nc[max(0, m.start() - 90):m.start()]).strip()[-80:]
            for k in m.group(1).split(","):
                uses.setdefault(k.strip(), []).append((os.path.basename(f), ctx))

    # ---- bbl order ----------------------------------------------------------
    order = []
    if os.path.exists(bbl):
        order = re.findall(r"\\bibitem(?:\[[^\]]*\])?\{([^}]*)\}", open(bbl, errors="ignore").read())
    num = {k: i + 1 for i, k in enumerate(order)}

    # ---- bib entries ----------------------------------------------------------
    entries, percent_keys = {}, []
    for b in bibs:
        if os.path.exists(b):
            e, p = parse_bib(b)
            entries.update(e); percent_keys += p
        else:
            print(f"!! bib file not found: {b}")

    problems = 0
    abbreviated = []
    def flag(msg):
        nonlocal problems
        problems += 1
        print("!! " + msg)

    print(f"tex files: {len(tex_files)}   bib files: {len(bibs)}   bbl items: {len(order)}   distinct cited keys: {len(uses)}")
    if order and len(order) != len(uses):
        flag(f"bbl has {len(order)} items but {len(uses)} distinct keys are cited")
    for k in uses:
        if k not in entries:
            flag(f"cited key not in any .bib: {k}")
        if order and k not in num:
            flag(f"cited key missing from .bbl (BibTeX skipped it?): {k}")
    for k in order:
        if k not in uses:
            flag(f"bbl item never cited: {k}")
    for k in percent_keys:
        flag(f"'%' inside entry body -> BibTeX will skip it: {k}")

    # ---- per-entry field checks ----------------------------------------------
    titles = {}
    for k, e in entries.items():
        if k not in uses:
            continue
        n, has_others = author_count(e.get("author", ""))
        if has_others:
            # The .bib cannot prove the true author count once it is abbreviated;
            # record it so the author can confirm the paper really has > max_authors.
            abbreviated.append(k)
        elif n > a.max_authors:
            flag(f"{k}: {n} authors listed in full -- IEEE uses first author + et al. beyond {a.max_authors}")
        if not e.get("year"):
            flag(f"{k}: no year")
        v = (e.get("journal", "") + e.get("booktitle", "")).lower()
        if not e.get("pages") and e["_type"] not in ("misc", "unpublished") and "arxiv" not in v and "arxiv" not in e.get("eprint", "").lower():
            flag(f"{k}: no pages ({e['_type']}, {v[:40]})")
        t = re.sub(r"\W", "", e.get("title", "").lower())[:50]
        if t:
            titles.setdefault(t, []).append(k)
    for t, ks in titles.items():
        if len(ks) > 1:
            flag(f"duplicate title across keys: {ks}")

    if abbreviated:
        print(f"info: {len(abbreviated)} entries use 'and others' (et al.): {abbreviated}\n"
              f"      IEEE allows this only past {a.max_authors} authors -- confirm each really has more, and never expand "
              f"them to fill a page.")

    # ---- contexts --------------------------------------------------------------
    if not a.quiet_contexts:
        print("\n  #  key                     where            context before \\cite")
        for k in (order if order else sorted(uses)):
            if k not in uses:
                continue
            for i, (f, ctx) in enumerate(uses[k]):
                print(f"{(num.get(k, '?') if i == 0 else ''):>3} {(k if i == 0 else ''):24s} {f[:16]:16s} ...{ctx}")

    print(f"\n{'OK: no citation problems found' if problems == 0 else f'{problems} problem(s) above'}")
    sys.exit(min(problems, 99))


if __name__ == "__main__":
    main()
