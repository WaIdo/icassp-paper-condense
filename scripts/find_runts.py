#!/usr/bin/env python3
"""Find paragraphs and captions whose last line holds only one or two words.

A one-word last line ("runt") wastes a whole line in a page-limited paper and
reads as sloppy. This maps every paragraph and every \\caption in the LaTeX
source to its last typeset line in the PDF, then reports the word count and
horizontal fill of that line.

The accounting rule that decides how many words to cut: with W words on the
last line and a full line of about N words (N ~ 10 at 9 pt), removing k words
leaves a new last line of roughly N + W - k words. Cutting 2-3 words is
usually optimal; cutting 5 or more just creates a new half-empty tail.

Usage:
  find_runts.py main.pdf --main main.tex          # discovers \\input/\\include files
  find_runts.py main.pdf --tex a.tex b.tex ...     # explicit list
  options: --max-words 2   (flag last lines with <= this many words; default 2)
           --min-words 6   (ignore blocks shorter than this)

Exit status is the number of flagged blocks (capped at 99), so it can gate a
build script. Requires poppler's pdftotext on PATH.
"""
import argparse, os, re, subprocess, sys


def discover_inputs(main_tex):
    """Return [main_tex] + every \\input/\\include target, recursively, in order."""
    seen, out = set(), []
    base = os.path.dirname(os.path.abspath(main_tex))

    def walk(path):
        path = os.path.abspath(path)
        if path in seen or not os.path.exists(path):
            return
        seen.add(path); out.append(path)
        src = re.sub(r"(?m)^\s*%.*$", "", open(path, errors="ignore").read())
        for m in re.finditer(r"\\(?:input|include)\{([^}]+)\}", src):
            t = m.group(1).strip()
            if not t.endswith(".tex"):
                t += ".tex"
            cand = t if os.path.isabs(t) else os.path.join(base, t)
            walk(cand)
    walk(main_tex)
    return out


def pdf_lines(pdf):
    xml = subprocess.run(["pdftotext", "-bbox", pdf, "-"], capture_output=True, text=True).stdout
    lines = []
    for pi, pg in enumerate(xml.split("<page ")[1:], 1):
        W = float(re.search(r'width="([\d.]+)"', pg).group(1))
        ws = [(float(a), float(b), float(c), float(d), e) for a, b, c, d, e in re.findall(
            r'<word xMin="(-?[\d.]+)" yMin="(-?[\d.]+)" xMax="(-?[\d.]+)" yMax="(-?[\d.]+)">(.*?)</word>', pg)]
        for side in ("L", "R"):
            col = sorted([w for w in ws if (w[0] < W / 2) == (side == "L")], key=lambda w: (w[1], w[0]))
            if not col:
                continue
            groups = []
            for w in col:
                if groups and abs(w[1] - groups[-1][0][1]) < 2.6:
                    groups[-1].append(w)
                else:
                    groups.append([w])
            L = min(min(x[0] for x in g) for g in groups)
            R = max(max(x[2] for x in g) for g in groups)
            for g in groups:
                g = sorted(g, key=lambda v: v[0])
                lines.append(dict(loc=f"p{pi}{side}", x0=g[0][0], x1=g[-1][2], L=L, R=R,
                                  txt=" ".join(x[4] for x in g), n=len(g)))
    return lines


def norm(s):
    s = re.sub(r"\\(?:emph|textbf|textit|ref|cite|label|url|eqref|autoref)\{[^{}]*\}", " ", s)
    s = re.sub(r"\\[a-zA-Z]+\*?", " ", s)
    return " ".join(re.sub(r"[^A-Za-z0-9]+", " ", s).split()).lower()


def brace_arg(src, i):
    """src[i] == '{' -> return (inner_text, index_of_closing_brace)."""
    d = 0
    for j in range(i, len(src)):
        if src[j] == "{":
            d += 1
        elif src[j] == "}":
            d -= 1
            if d == 0:
                return src[i + 1:j], j
    return src[i + 1:], len(src)


def blocks_from(tex_files, min_words):
    blocks = []
    for f in tex_files:
        src = re.sub(r"(?m)^\s*%.*$", "", open(f, errors="ignore").read())
        if "\\begin{document}" in src:
            src = src.split("\\begin{document}", 1)[1]
        name = os.path.basename(f)
        for m in re.finditer(r"\\caption\{", src):
            inner, j = brace_arg(src, m.end() - 1)
            lab = re.search(r"\\label\{([^}]*)\}", src[j:j + 300])
            blocks.append((f"caption {lab.group(1) if lab else name}", inner))
        body = re.sub(r"\\begin\{(figure|table)\*?\}.*?\\end\{\1\*?\}", " ", src, flags=re.S)
        body = re.sub(r"\\begin\{(equation|align|gather)\*?\}.*?\\end\{\1\*?\}", " ", body, flags=re.S)
        body = re.sub(r"\\input\{[^}]*\}|\\include\{[^}]*\}", " ", body)
        for para in re.split(r"\n\s*\n", body):
            p = para.strip()
            if not p or p.startswith(("\\section", "\\subsection", "\\subsubsection", "\\begin", "\\end",
                                      "\\ifdefined", "\\documentclass", "\\usepackage", "\\title", "\\name",
                                      "\\address", "\\maketitle", "\\bibliography", "\\newcommand", "\\def",
                                      "\\renewcommand", "\\setlength", "\\let", "\\long", "\\makeat", "\\@")):
                continue
            p = re.sub(r"^\\textbf\{[^}]*\}\s*", "", p)
            if len(norm(p).split()) >= min_words:
                blocks.append((f"para {name}", p))
    return blocks


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("pdf")
    ap.add_argument("--main", help="main .tex; its \\input/\\include files are discovered")
    ap.add_argument("--tex", nargs="*", help="explicit .tex files")
    ap.add_argument("--max-words", type=int, default=2)
    ap.add_argument("--min-words", type=int, default=6)
    ap.add_argument("--show-all", action="store_true", help="print every block, not only flagged ones")
    a = ap.parse_args()
    if not a.main and not a.tex:
        sys.exit("give --main main.tex or --tex files")
    tex = discover_inputs(a.main) if a.main else a.tex
    lines = pdf_lines(a.pdf)
    blocks = blocks_from(tex, a.min_words)

    flagged = 0
    unmatched = 0
    rows = []
    for kind, b in blocks:
        words = norm(b).split()
        best = None
        for k in (6, 5, 4, 3, 2):
            tail = words[-k:]
            for i, r in enumerate(lines):
                cat = []
                for j in range(max(0, i - 3), i + 1):
                    if lines[j]["loc"] == r["loc"] or j == i:
                        cat += norm(lines[j]["txt"]).split()
                if len(cat) >= len(tail) and cat[-len(tail):] == tail:
                    best = r; break
            if best:
                break
        if not best:
            unmatched += 1
            rows.append((kind, "??", None, None, " ".join(words[-5:]), False))
            continue
        fill = (best["x1"] - best["x0"]) / (best["R"] - best["L"]) * 100
        flag = best["n"] <= a.max_words
        flagged += flag
        rows.append((kind, best["loc"], best["n"], fill, best["txt"][:46], flag))

    print(f"{'block':28s} {'loc':6s} {'words':>5s} {'fill':>6s}  last line")
    for kind, loc, n, fill, txt, flag in rows:
        if not (flag or a.show_all or n is None):
            continue
        if n is None:
            print(f"{kind:28s} {loc:6s} {'-':>5s} {'-':>6s}  ...{txt}   (not matched in PDF)")
        else:
            mark = f"   <<< {n}-word last line" if flag else ("   << 3 words" if n == 3 and fill < 32 else "")
            print(f"{kind:28s} {loc:6s} {n:5d} {fill:5.1f}%  {txt!r}{mark}")
    print(f"\nblocks {len(blocks)}, flagged (<= {a.max_words} words) {flagged}, unmatched {unmatched}")
    sys.exit(min(flagged, 99))


if __name__ == "__main__":
    main()
