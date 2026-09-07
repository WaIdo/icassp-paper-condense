#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
# Copyright (c) 2026 WaIdo (github.com/WaIdo)
# Part of the icassp-paper-condense skill: https://github.com/WaIdo/icassp-paper-condense
"""List every number that disappeared from, or appeared in, a paper between two PDFs.

This is the last gate after any edit: compare the body pages of the previous
PDF and the current one, and print the multiset difference of numeric tokens.
Every entry in the "lost" list must be explainable (a citation renumbered, a
model name moved, a value corrected); one you cannot explain is a value you
deleted by accident.

Usage:
  diff_numbers.py old.pdf new.pdf [--pages 4] [--min-digits 2]

Requires PyMuPDF.
"""
import argparse, collections, re, sys

try:
    import fitz
except ImportError:
    sys.exit("PyMuPDF missing: pip install pymupdf")


def numbers(pdf, pages, min_digits):
    doc = fitz.open(pdf)
    t = "".join(doc[i].get_text() for i in range(min(pages, len(doc)))).replace("−", "-")
    dec = re.findall(r"-?\d+\.\d+", t)
    ints = re.findall(r"\b\d{%d,}\b" % min_digits, t)
    return collections.Counter(dec), collections.Counter(ints)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("old"); ap.add_argument("new")
    ap.add_argument("--pages", type=int, default=4, help="compare the first N pages (the technical content)")
    ap.add_argument("--min-digits", type=int, default=2)
    a = ap.parse_args()
    od, oi = numbers(a.old, a.pages, a.min_digits)
    nd, ni = numbers(a.new, a.pages, a.min_digits)

    def show(label, old, new):
        lost = sorted((k, old[k], new[k]) for k in old if new[k] < old[k])
        gained = sorted((k, old[k], new[k]) for k in new if new[k] > old[k])
        print(f"{label}: lost {len(lost)}, gained {len(gained)}")
        for k, o, n in lost:
            print(f"   - {k}  ({o} -> {n})")
        for k, o, n in gained:
            print(f"   + {k}  ({o} -> {n})")
        return len(lost) + len(gained)

    changed = show("decimals", od, nd) + show("integers", oi, ni)
    print("\nexplain every line above before accepting the edit." if changed else "\nno numeric change on the compared pages.")


if __name__ == "__main__":
    main()
