#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
# Copyright (c) 2026 WaIdo (github.com/WaIdo)
# Part of the icassp-paper-condense skill: https://github.com/WaIdo/icassp-paper-condense
"""Measure a directory of accepted papers from the target venue.

Most typesetting arguments end with "what do accepted papers actually do?"
Rather than assert from memory, measure them. For every PDF in the directory
this prints, per paper:

  * pages, title first-line y, title-block line count, sizes used in the block
  * abstract line count and ink height (mm)
  * last page: right-column bottom and its gap to the text block
  * median gap between consecutive reference entries (mm) -- the \\itemsep proxy
  * smallest text sizes, and the smallest size used inside tables (heuristic)
  * semicolon and colon density per 1000 words in the body
  * figure/table first-citation inversions

and closes with the median and max of each column. Point the paper you are
condensing at the same script (pass its PDF as an extra argument) to see
where it sits against the venue.

Usage:
  corpus_baseline.py papers/ICASSP2026/ [--also main.pdf]
"""
import argparse, collections, glob, os, re, statistics as st, sys

try:
    import fitz
except ImportError:
    sys.exit("PyMuPDF missing: pip install pymupdf")

MM = 25.4 / 72.0


def lines_of(page):
    out = []
    for b in page.get_text("dict")["blocks"]:
        if b.get("type", 0) != 0:
            continue
        for l in b["lines"]:
            x0, y0, x1, y1 = l["bbox"]
            out.append(dict(x0=x0 * MM, y0=y0 * MM, x1=x1 * MM, y1=y1 * MM,
                            text="".join(s["text"] for s in l["spans"]), spans=l["spans"]))
    return out


HEAD_RE = re.compile(r"^\s*\d+(\.\d+)*\.?\s+\S")


def heading_gaps(doc):
    """Extra white above/below numbered section headings, in pt.

    Reported *net of the paper's own in-paragraph line gap*, so a 9 pt and a
    10 pt paper are comparable.  Returns (n, median_above, median_below,
    per-heading rows) or (0, None, None, []) when no heading is recognised.
    """
    cols = []
    for page in doc:
        w = page.rect.width
        left, right = [], []
        for b in page.get_text("dict")["blocks"]:
            if b.get("type", 0) != 0:
                continue
            for ln in b["lines"]:
                t = "".join(s["text"] for s in ln["spans"]).strip()
                if not t:
                    continue
                x0, y0, x1, y1 = ln["bbox"]
                sp = max(ln["spans"], key=lambda s: len(s["text"]))
                (left if (x0 + x1) / 2 < w / 2 else right).append(
                    dict(y0=y0, y1=y1, t=t, size=sp["size"], font=sp["font"], blk=b["number"]))
        for c in (left, right):
            c.sort(key=lambda r: r["y0"])
            if c:
                cols.append(c)
    if not cols:
        return 0, None, None, []
    hist = {}
    for c in cols:
        for r in c:
            hist[round(r["size"] * 2) / 2] = hist.get(round(r["size"] * 2) / 2, 0) + len(r["t"])
    body = max(hist, key=hist.get)
    gaps = [b["y0"] - a["y1"] for c in cols for a, b in zip(c, c[1:])
            if a["blk"] == b["blk"] and abs(a["size"] - body) < .3
            and abs(b["size"] - body) < .3 and 0 <= b["y0"] - a["y1"] < 8]
    if not gaps:
        return 0, None, None, []
    lg = st.median(gaps)
    rows = []
    for c in cols:
        for i in range(1, len(c) - 1):
            r = c[i]
            if not HEAD_RE.match(r["t"]) or len(r["t"]) > 60:
                continue
            if not any(k in r["font"] for k in ("Medi", "Bold", "-B")):
                continue
            if not any(k in r["font"] for k in ("Rom", "Times", "Nimbus", "TeX", "Termes")):
                continue
            if abs(r["size"] - body) > 1.5:
                continue
            ab, be = r["y0"] - c[i - 1]["y1"], c[i + 1]["y0"] - r["y1"]
            if not (0 <= ab < 45 and 0 <= be < 45):
                continue
            rows.append((r["t"][:40], round(ab - lg, 2), round(be - lg, 2)))
    if not rows:
        return 0, None, None, []
    return (len(rows), round(st.median([x[1] for x in rows]), 2),
            round(st.median([x[2] for x in rows]), 2), rows)


def measure(pdf):
    d = fitz.open(pdf)
    mid = d[0].rect.width * MM / 2
    r = dict(file=os.path.basename(pdf), pages=len(d))
    p1 = lines_of(d[0])
    left = sorted([l for l in p1 if l["x0"] < mid], key=lambda l: l["y0"])
    # title block / abstract
    try:
        i0 = next(i for i, l in enumerate(left) if l["text"].strip().upper().startswith("ABSTRACT"))
        i1 = next(i for i, l in enumerate(left) if i > i0 and ("ndex Terms" in l["text"] or re.match(r"\s*1\.?\s+[A-Z]", l["text"])))
        ab = left[i0 + 1:i1]
        r["abs_lines"] = len(ab)
        r["abs_mm"] = round(ab[-1]["y1"] - ab[0]["y0"], 1)
        tb = sorted([l for l in p1 if l["y1"] < left[i0]["y0"] - 1], key=lambda l: l["y0"])
        r["title_y"] = round(tb[0]["y0"], 1) if tb else None
        r["tb_lines"] = len(tb)
        r["tb_sizes"] = sorted({round(max(s["size"] for s in l["spans"]), 0) for l in tb})
    except StopIteration:
        r.update(abs_lines=None, abs_mm=None, title_y=None, tb_lines=None, tb_sizes=None)
    # columns
    bottoms = []
    for p in d:
        ls = lines_of(p)
        L = [l["y1"] for l in ls if l["x0"] < mid]; R = [l["y1"] for l in ls if l["x0"] >= mid]
        bottoms.append((max(L) if L else 0, max(R) if R else 0))
    ref = max(b for pair in bottoms[:-1] for b in pair) if len(bottoms) > 1 else bottoms[0][0]
    r["last_gap_mm"] = round(ref - bottoms[-1][1], 1) if bottoms[-1][1] else None
    # reference itemsep proxy: gap from previous line bottom to next "[n]" line top, same column
    gaps = []
    for p in d[max(0, len(d) - 2):]:
        prev = None; prevcol = None
        for l in sorted(lines_of(p), key=lambda l: (l["x0"] >= mid, l["y0"])):
            col = l["x0"] >= mid
            if re.match(r"^\[\d+\]", l["text"].strip()) and prev is not None and prevcol == col:
                g = l["y0"] - prev
                if 0 < g < 8:
                    gaps.append(g)
            prev, prevcol = l["y1"], col
    r["ref_gap_mm"] = round(st.median(gaps), 2) if gaps else None
    # sizes
    sizes = collections.Counter()
    body_words = 0; semi = 0; colon = 0
    texts = []
    for pi, p in enumerate(d):
        for l in lines_of(p):
            for s in l["spans"]:
                if len(s["text"].strip()) > 3:
                    sizes[round(s["size"], 1)] += 1
        texts.append(p.get_text())
    body = "".join(texts[:-1]) if len(texts) > 1 else texts[0]
    body = re.sub(r"\[\d+[^\]]*\]", "", body)
    body_words = len(re.findall(r"[A-Za-z][A-Za-z-]+", body)) or 1
    r["semi_per_k"] = round(1000 * body.count(";") / body_words, 2)
    r["colon_per_k"] = round(1000 * body.count(":") / body_words, 2)
    r["min_size"] = min(sizes) if sizes else None
    r["sizes_lt9"] = sorted(k for k in sizes if k < 8.9)[:4]
    # float citation order
    seq = []
    for m in re.finditer(r"\b(Figs?|Tables?)\.?\s*(\d+)", body):
        t = ("F" if m.group(1).startswith("Fig") else "T") + m.group(2)
        if t not in seq:
            seq.append(t)
    fn = [int(s[1:]) for s in seq if s[0] == "F"]; tn = [int(s[1:]) for s in seq if s[0] == "T"]
    r["float_inv"] = sum(1 for i in range(len(fn) - 1) if fn[i + 1] < fn[i]) + sum(1 for i in range(len(tn) - 1) if tn[i + 1] < tn[i])
    # reference order inversions
    order = []
    for m in re.finditer(r"\[(\d+(?:\s*[-–,]\s*\d+)*)\]", "".join(texts[:-1]) if len(texts) > 1 else texts[0]):
        for n in re.findall(r"\d+", m.group(1)):
            n = int(n)
            if n not in order:
                order.append(n)
    r["ref_inv"] = sum(1 for i in range(len(order) - 1) if order[i + 1] < order[i])
    n, ab, be = heading_gaps(d)[:3]
    r["head_ab_pt"], r["head_be_pt"] = ab, be
    return r


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("corpus_dir")
    ap.add_argument("--also", nargs="*", default=[], help="extra PDFs (e.g. your own paper) listed after the corpus")
    a = ap.parse_args()
    pdfs = sorted(glob.glob(os.path.join(a.corpus_dir, "*.pdf")))
    if not pdfs:
        sys.exit("no PDFs in " + a.corpus_dir)
    rows = [measure(p) for p in pdfs]
    extra = [measure(p) for p in a.also]
    cols = ["pages", "title_y", "tb_lines", "tb_sizes", "abs_lines", "abs_mm", "last_gap_mm", "ref_gap_mm",
            "head_ab_pt", "head_be_pt", "min_size", "semi_per_k", "colon_per_k", "float_inv", "ref_inv"]
    hdr = f"{'file':24s} " + " ".join(f"{c:>11s}" for c in cols)
    print(hdr)
    for r in rows + extra:
        print(f"{r['file'][:24]:24s} " + " ".join(f"{str(r.get(c)):>11s}" for c in cols))
    print("-" * len(hdr))
    for lab, fn in (("median", st.median), ("max", max), ("min", min)):
        vals = []
        for c in cols:
            xs = [r[c] for r in rows if isinstance(r.get(c), (int, float))]
            vals.append(f"{fn(xs):>11.2f}" if xs and c not in ("tb_sizes",) else f"{'':>11s}")
        print(f"{lab:24s} " + " ".join(vals))
    print("\ncolumns: title_y = first title line y (mm); tb_lines = lines in the title block; abs_mm = abstract ink height;"
          "\nlast_gap_mm = last page right-column gap to text block; ref_gap_mm = median gap before each [n] entry;"
          "\nhead_ab_pt / head_be_pt = median extra white above / below a numbered section heading, net of that paper's own line gap;"
          "\nsemi/colon_per_k = per 1000 body words; *_inv = first-citation order inversions (figures+tables / references).")


if __name__ == "__main__":
    main()
