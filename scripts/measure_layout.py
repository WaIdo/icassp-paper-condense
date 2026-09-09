#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
# Copyright (c) 2026 WaIdo (github.com/WaIdo)
# Part of the icassp-paper-condense skill: https://github.com/WaIdo/icassp-paper-condense
"""One-shot layout report for a two-column conference PDF (ICASSP / spconf).

Reports the things that decide whether a page-limited paper is actually
compliant and actually full, so every edit can be checked against numbers
instead of impressions:

  * page count and page size
  * per-page, per-column bottom y (mm) and the last column's gap
  * LaTeX log counts: Overfull / Underfull hbox, undefined references
  * BibTeX warnings (from the .blg next to the PDF, if present)
  * references: count, cited set, orphans, "[?]", first-citation inversions
  * figure / table first-citation order
  * abstract block: line count and height (kit limit is 80 mm)
  * text-span font sizes, with the smallest sizes listed by location
  * title block: line count and width of each line
  * page numbers (the kit forbids them)

Usage:
  measure_layout.py main.pdf [--target-pages 5] [--body-pages 4] [--json]

Requires: PyMuPDF (pip install pymupdf) and poppler's pdfinfo on PATH.
"""
import statistics as st
import argparse, collections, json, os, re, subprocess, sys

try:
    import fitz  # PyMuPDF
except ImportError:
    sys.exit("PyMuPDF missing: pip install pymupdf")

MM = 25.4 / 72.0


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


def lines_of(page):
    """Yield (x0, y0, x1, y1, text, size_of_first_span, spans) for each text line, in mm."""
    out = []
    for b in page.get_text("dict")["blocks"]:
        if b.get("type", 0) != 0:
            continue
        for l in b["lines"]:
            x0, y0, x1, y1 = l["bbox"]
            text = "".join(s["text"] for s in l["spans"])
            out.append(dict(x0=x0 * MM, y0=y0 * MM, x1=x1 * MM, y1=y1 * MM,
                            text=text, spans=l["spans"]))
    return out


def log_counts(log_path):
    if not log_path or not os.path.exists(log_path):
        return None
    s = open(log_path, errors="ignore").read()
    return dict(overfull=len(re.findall(r"Overfull \\hbox", s)),
                underfull_hbox=len(re.findall(r"Underfull \\hbox", s)),
                underfull_vbox=len(re.findall(r"Underfull \\vbox", s)),
                undefined=len(re.findall(r"undefined", s)))


def blg_warnings(blg_path):
    if not blg_path or not os.path.exists(blg_path):
        return None
    s = open(blg_path, errors="ignore").read()
    return len(re.findall(r"(?m)^Warning--", s)) + len(re.findall(r"You're missing", s))


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("pdf")
    ap.add_argument("--target-pages", type=int, default=5, help="allowed total pages (ICASSP: 5)")
    ap.add_argument("--body-pages", type=int, default=4, help="pages that may hold technical content (ICASSP: 4)")
    ap.add_argument("--abstract-limit-mm", type=float, default=80.0)
    ap.add_argument("--min-font-pt", type=float, default=9.0)
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args()

    doc = fitz.open(a.pdf)
    stem = os.path.splitext(a.pdf)[0]
    R = {}
    R["pages"] = len(doc)
    R["page_size_pt"] = [round(doc[0].rect.width, 1), round(doc[0].rect.height, 1)]
    R["is_letter"] = abs(doc[0].rect.width - 612) < 1 and abs(doc[0].rect.height - 792) < 1

    # ---- columns ---------------------------------------------------------
    mid = doc[0].rect.width * MM / 2
    cols = []
    all_lines = []
    for pi, page in enumerate(doc):
        ls = lines_of(page)
        all_lines.append(ls)
        L = [l["y1"] for l in ls if l["x0"] < mid]
        Rr = [l["y1"] for l in ls if l["x0"] >= mid]
        cols.append(dict(page=pi + 1, left_bottom=round(max(L), 1) if L else None,
                         right_bottom=round(max(Rr), 1) if Rr else None))
    R["columns"] = cols
    full_bottoms = [c[k] for c in cols[:-1] for k in ("left_bottom", "right_bottom") if c[k]]
    ref_bottom = max(full_bottoms) if full_bottoms else None
    last = cols[-1]
    R["text_block_bottom_mm"] = round(ref_bottom, 1) if ref_bottom else None
    R["last_column_gap_mm"] = (round(ref_bottom - last["right_bottom"], 1)
                               if ref_bottom and last["right_bottom"] else None)

    # ---- page numbers (forbidden) ---------------------------------------
    pn = []
    if ref_bottom:
        for pi, ls in enumerate(all_lines):
            for l in ls:
                if l["y0"] > ref_bottom + 1.5 and re.fullmatch(r"\s*\d{1,3}\s*", l["text"]):
                    pn.append(dict(page=pi + 1, text=l["text"].strip()))
    R["page_numbers_found"] = pn

    # ---- section-heading spacing ----------------------------------------
    hn, hab, hbe, hrows = heading_gaps(doc)
    R["heading_spacing"] = dict(count=hn, extra_above_pt=hab, extra_below_pt=hbe,
                                headings=[dict(text=t, above_pt=a2, below_pt=b2) for t, a2, b2 in hrows])

    # ---- references ------------------------------------------------------
    texts = [p.get_text() for p in doc]
    ref_page = next((i for i, t in enumerate(texts) if re.search(r"\n\s*\d*\.?\s*REFERENCES\s*\n", t)), None)
    body_pages = list(range(0, ref_page + 1)) if ref_page is not None else list(range(len(doc)))
    body = "".join(texts[i] for i in range(0, min(len(doc), a.body_pages)))
    body_upto_refs = "".join(texts[i] for i in body_pages)
    if ref_page is not None:
        pre, _, _ = texts[ref_page].partition("REFERENCES")
        body_upto_refs = "".join(texts[:ref_page]) + pre
    ref_text = "".join(texts[ref_page:]) if ref_page is not None else ""
    ref_entries = re.findall(r"(?m)^\[(\d+)\]", ref_text)
    n_refs = len(set(ref_entries))
    order = []
    for m in re.finditer(r"\[(\d+(?:\s*[-–,]\s*\d+)*)\]", body_upto_refs):
        for n in re.findall(r"\d+", m.group(1)):
            n = int(n)
            if n not in order:
                order.append(n)
    inversions = [(order[i], order[i + 1]) for i in range(len(order) - 1) if order[i + 1] < order[i]]
    R["references"] = dict(
        list_count=n_refs,
        cited_count=len(order),
        uncited=[i for i in range(1, n_refs + 1) if i not in order],
        cited_beyond_list=[i for i in order if i > n_refs],
        unresolved_marks="[?]" in body_upto_refs,
        first_citation_inversions=inversions,
        references_start_page=(ref_page + 1) if ref_page is not None else None,
    )

    # ---- floats first-citation order -------------------------------------
    seq = []
    for m in re.finditer(r"\b(Figs?|Tables?)\.?\s*(\d+)", body_upto_refs):
        t = ("F" if m.group(1).startswith("Fig") else "T") + m.group(2)
        if t not in seq:
            seq.append(t)
    fig_nums = [int(s[1:]) for s in seq if s[0] == "F"]
    tab_nums = [int(s[1:]) for s in seq if s[0] == "T"]
    R["float_citation_order"] = dict(sequence=seq,
                                     figures_ascending=fig_nums == sorted(fig_nums),
                                     tables_ascending=tab_nums == sorted(tab_nums))

    # ---- what is on pages after body-pages ----------------------------------
    extra = []
    for i in range(a.body_pages, len(doc)):
        heads = re.findall(r"(?m)^\s*(\d+\.\s+[A-Z][A-Z &-]{3,})\s*$", texts[i])
        extra.append(dict(page=i + 1, headings=heads))
    R["pages_beyond_body"] = extra

    # ---- abstract ----------------------------------------------------------
    p1 = sorted([l for l in all_lines[0] if l["x0"] < mid], key=lambda l: l["y0"])
    try:
        i0 = next(i for i, l in enumerate(p1) if l["text"].strip().upper() == "ABSTRACT")
        i1 = next(i for i, l in enumerate(p1) if i > i0 and ("Index Terms" in l["text"] or re.match(r"\s*1\.\s", l["text"])))
        ab = p1[i0 + 1:i1]
        pitch = (ab[-1]["y0"] - ab[0]["y0"]) / (len(ab) - 1) if len(ab) > 1 else 0
        R["abstract"] = dict(lines=len(ab), ink_height_mm=round(ab[-1]["y1"] - ab[0]["y0"], 1),
                             lines_times_pitch_mm=round(len(ab) * pitch, 1),
                             limit_mm=a.abstract_limit_mm)
    except StopIteration:
        R["abstract"] = None

    # ---- title block --------------------------------------------------------
    if R["abstract"] is not None:
        abs_y = p1[i0]["y0"]
        tb = [l for l in all_lines[0] if l["y1"] < abs_y - 1]
        tb = sorted(tb, key=lambda l: l["y0"])
        R["title_block"] = dict(lines=len(tb), first_line_y_mm=round(tb[0]["y0"], 1) if tb else None,
                                widths_mm=[round(l["x1"] - l["x0"], 1) for l in tb],
                                sizes_pt=[round(max(sp["size"] for sp in l["spans"]), 1) for l in tb])

    # ---- font sizes ---------------------------------------------------------
    hist = collections.Counter()
    small = []
    for pi, ls in enumerate(all_lines):
        for l in ls:
            for s in l["spans"]:
                t = s["text"].strip()
                if len(t) > 5:
                    sz = round(s["size"], 1)
                    hist[sz] += 1
                    if sz < a.min_font_pt - 0.15 and len(t) > 8:
                        small.append(dict(page=pi + 1, size=sz, text=t[:60]))
    R["font_sizes"] = dict(histogram=dict(sorted(hist.items())),
                           below_min=small[:60], below_min_count=len(small))

    # ---- log / blg ----------------------------------------------------------
    R["latex_log"] = log_counts(stem + ".log")
    R["bibtex_warnings"] = blg_warnings(stem + ".blg")

    if a.json:
        print(json.dumps(R, ensure_ascii=False, indent=1))
        return

    # ---- human report --------------------------------------------------------
    ok = lambda c: "OK " if c else "!! "
    print(f"{ok(R['pages'] <= a.target_pages)}pages {R['pages']} (limit {a.target_pages})   "
          f"{ok(R['is_letter'])}page size {R['page_size_pt']} pt (letter = 612x792)")
    print("    column bottoms (mm):", "  ".join(
        f"p{c['page']} L{c['left_bottom']} R{c['right_bottom']}" for c in cols))
    print(f"    text block bottom ~{R['text_block_bottom_mm']} mm; last column gap {R['last_column_gap_mm']} mm")
    if R["latex_log"]:
        L = R["latex_log"]
        print(f"{ok(L['overfull'] == 0 and L['undefined'] == 0)}log: Overfull {L['overfull']}  "
              f"Underfull-hbox {L['underfull_hbox']}  Underfull-vbox {L['underfull_vbox']}  undefined {L['undefined']}")
    else:
        print("    log: (no .log next to the PDF)")
    if R["bibtex_warnings"] is not None:
        print(f"{ok(R['bibtex_warnings'] == 0)}bibtex warnings {R['bibtex_warnings']}")
    rr = R["references"]
    print(f"{ok(not rr['uncited'] and not rr['unresolved_marks'] and not rr['cited_beyond_list'])}"
          f"references: list {rr['list_count']}, cited {rr['cited_count']}, uncited {rr['uncited']}, "
          f"[?] {rr['unresolved_marks']}, start page {rr['references_start_page']}")
    print(f"    first-citation inversions {rr['first_citation_inversions']} "
          f"(2 of 7 accepted ICASSP 2026 papers have one; floats cite when declared, not where placed)")
    fo = R["float_citation_order"]
    print(f"{ok(fo['figures_ascending'] and fo['tables_ascending'])}float first-citation order {fo['sequence']}")
    for e in R["pages_beyond_body"]:
        bad = [h for h in e["headings"] if not re.search(r"REFERENCE|ACKNOWLEDG|COMPLIANCE|ETHIC", h)]
        print(f"{ok(not bad)}page {e['page']} headings: {e['headings']}"
              + ("   <-- technical content beyond the body-page limit" if bad else ""))
    if R["abstract"]:
        ab = R["abstract"]
        print(f"{ok(ab['ink_height_mm'] <= a.abstract_limit_mm + 0.5)}abstract: {ab['lines']} lines, "
              f"ink height {ab['ink_height_mm']} mm, lines x pitch {ab['lines_times_pitch_mm']} mm (limit {a.abstract_limit_mm})")
    if R.get("title_block"):
        tb = R["title_block"]
        print(f"    title block: {tb['lines']} lines, first line at y={tb['first_line_y_mm']} mm "
              f"(accepted ICASSP 2026 papers: 33.1-34.1), widths {tb['widths_mm']}, sizes {tb['sizes_pt']}")
    print(f"{ok(not pn)}page numbers found: {pn if pn else 'none'}")
    hs = R["heading_spacing"]
    if hs["count"]:
        lo = hs["extra_above_pt"] >= 10.5 and hs["extra_below_pt"] >= 4.3
        print(f"{ok(lo)}heading spacing: {hs['count']} headings, extra white above "
              f"{hs['extra_above_pt']} pt, below {hs['extra_below_pt']} pt "
              f"(accepted ICASSP 2026: above 10.5-17.5, below 4.3-9.4)")
        if not lo:
            print("    tighter than every paper in the corpus -- justify it by the "
                  "page it buys, and report it to the author")
    fs = R["font_sizes"]
    print(f"    font sizes (spans >5 chars): {fs['histogram']}")
    if fs["below_min"]:
        print(f"    spans below {a.min_font_pt}pt with >8 chars: {fs['below_min_count']} "
              f"(table bodies and in-figure labels are normally smaller; captions and body must not be)")
        for s in fs["below_min"][:12]:
            print(f"      p{s['page']} {s['size']}pt  {s['text']}")


if __name__ == "__main__":
    main()
