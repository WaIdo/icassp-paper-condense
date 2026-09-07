#!/usr/bin/env bash
# SPDX-License-Identifier: MIT
# Copyright (c) 2026 WaIdo (github.com/WaIdo)
# Part of the icassp-paper-condense skill: https://github.com/WaIdo/icassp-paper-condense
# Rebuild the paper and run every check that must pass after an edit.
#
#   verify_all.sh main.tex [--backup previous.pdf] [--target-pages 5] [--body-pages 4]
#
# Exit status is non-zero if any gate fails. Run it after EVERY edit; never
# stack two edits without a rebuild in between -- when the second one breaks
# the layout you will not know which of the two did it.
set -u
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
MAIN="${1:?usage: verify_all.sh main.tex [--backup old.pdf] [--target-pages N] [--body-pages N]}"; shift
BACKUP=""; TP=5; BP=4
while [ $# -gt 0 ]; do
  case "$1" in
    --backup) BACKUP="$2"; shift 2;;
    --target-pages) TP="$2"; shift 2;;
    --body-pages) BP="$2"; shift 2;;
    *) echo "unknown option $1"; exit 2;;
  esac
done
DIR="$(cd "$(dirname "$MAIN")" && pwd)"; STEM="$(basename "${MAIN%.tex}")"
cd "$DIR" || exit 2
FAIL=0

echo "== build"
latexmk -pdf -interaction=nonstopmode "$STEM.tex" >/tmp/verify_all_latexmk.log 2>&1
if [ $? -ne 0 ]; then echo "!! latexmk failed (see /tmp/verify_all_latexmk.log)"; FAIL=1; fi
# BibTeX's own exit status is hidden inside latexmk; check its log directly.
if [ -f "$STEM.blg" ] && grep -q "You're missing\|I found no\|Warning--" "$STEM.blg"; then
  echo "!! BibTeX reported problems:"; grep "You're missing\|I found no\|Warning--" "$STEM.blg" | head -5; FAIL=1
fi

echo "== layout"
python3 "$HERE/measure_layout.py" "$STEM.pdf" --target-pages "$TP" --body-pages "$BP" | tee /tmp/verify_all_layout.txt
grep -q '^!! ' /tmp/verify_all_layout.txt && FAIL=1

echo "== short last lines"
python3 "$HERE/find_runts.py" "$STEM.pdf" --main "$STEM.tex"; RC=$?
[ "$RC" -ne 0 ] && FAIL=1

echo "== citations"
python3 "$HERE/check_citations.py" --main "$STEM.tex" --quiet-contexts; RC=$?
[ "$RC" -ne 0 ] && FAIL=1

if [ -n "$BACKUP" ]; then
  echo "== numbers vs $BACKUP"
  python3 "$HERE/diff_numbers.py" "$BACKUP" "$STEM.pdf" --pages "$BP"
fi

echo
if [ "$FAIL" -eq 0 ]; then echo "ALL GATES PASSED"; else echo "SOME GATES FAILED (see !! lines above)"; fi
exit $FAIL
